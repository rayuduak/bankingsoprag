"""Simple Chroma wrapper for upsert and similarity search."""
from typing import List, Dict, Optional
import math
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except Exception:
    CHROMADB_AVAILABLE = False


def _cosine(a, b):
    # assume lists
    dot = sum(x * y for x, y in zip(a, b))
    maga = math.sqrt(sum(x * x for x in a))
    magb = math.sqrt(sum(y * y for y in b))
    if maga == 0 or magb == 0:
        return 0.0
    return dot / (maga * magb)


class ChromaClientWrapper:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self._memory_docs = []  # fallback store
        self._sources = {}  # map source -> count
        self.collection = None
        self.meta_collection = None
        print(f"Initializing ChromaClientWrapper with {persist_directory}")
        if CHROMADB_AVAILABLE:
            try:
                # Modern Chroma (0.4+) uses PersistentClient
                self.client = chromadb.PersistentClient(path=persist_directory)
                self.collection = self.client.get_or_create_collection("usecases")
                self.meta_collection = self.client.get_or_create_collection("file_metadata")
                print("ChromaDB PersistentClient initialized. Collections 'usecases' and 'file_metadata' ready.")
            except Exception as e:
                print(f"Error initializing ChromaDB: {e}. Falling back to memory.")
                self.collection = None
        else:
            print("ChromaDB NOT AVAILABLE. Using memory store.")
            self.collection = None

    def reset_collections(self):
        """Delete all documents from both collections."""
        if self.collection:
            try:
                # Get all IDs and delete
                res = self.collection.get()
                if res['ids']:
                    self.collection.delete(ids=res['ids'])
                print("Main collection 'usecases' cleared.")
            except Exception as e:
                print(f"Failed to clear main collection: {e}")
        
        if self.meta_collection:
            try:
                res = self.meta_collection.get()
                if res['ids']:
                    self.meta_collection.delete(ids=res['ids'])
                print("Metadata collection 'file_metadata' cleared.")
            except Exception as e:
                print(f"Failed to clear metadata collection: {e}")
        
        self._sources = {}
        self._memory_docs = []

    def save_file_metadata(self, filename: str, size: int, timestamp: str):
        """Store file-level metadata in the meta_collection."""
        if self.meta_collection:
            try:
                self.meta_collection.upsert(
                    ids=[filename],
                    documents=[f"File: {filename}, Size: {size}, Uploaded: {timestamp}"],
                    metadatas=[{"filename": filename, "size": size, "timestamp": timestamp}]
                )
                print(f"Metadata saved for {filename}")
            except Exception as e:
                print(f"Failed to save file metadata: {e}")

    def upsert_documents(self, docs: List[Dict], embeddings: Optional[List[List[float]]] = None):
        ids = [d["id"] for d in docs]
        texts = [d["text"] for d in docs]
        metadatas = [d.get("metadata", {}) for d in docs]
        
        print(f"Upserting {len(ids)} documents to Chroma...")
        if self.collection is not None:
            try:
                # In Chroma 0.5+, embeddings are often passed separately or handled by the collection's embedding function
                # For 1.5.0 (which might be a pre-release or specific build), let's ensure we match the expected signature
                kwargs = {"ids": ids, "documents": texts, "metadatas": metadatas}
                if embeddings is not None:
                    kwargs["embeddings"] = embeddings
                
                self.collection.upsert(**kwargs)
                print("Chroma upsert successful.")
                return
            except Exception as e:
                print(f"Chroma upsert failed: {e}. Falling back to memory.")
                import traceback
                traceback.print_exc()

        # memory fallback: store embeddings (if provided) or placeholder
        for i, d in enumerate(docs):
            emb = None
            if embeddings is not None and i < len(embeddings):
                emb = embeddings[i]
            self._memory_docs.append({"id": d["id"], "text": d["text"], "metadata": metadatas[i], "embedding": emb})
            # track source counts for listing
            src = metadatas[i].get("source") if isinstance(metadatas[i], dict) else None
            if src:
                self._sources[src] = self._sources.get(src, 0) + 1

    def similarity_search_by_embedding(self, embedding, top_k: int = 4):
        if self.collection is not None:
            try:
                # Results for 0.4+/0.5+ are dicts with list of lists
                results = self.collection.query(query_embeddings=[embedding], n_results=top_k)
                docs = []
                # Check for nested results
                ids = results.get("ids", [[]])[0]
                documents = results.get("documents", [[]])[0]
                distances = results.get("distances", [[]])[0]
                
                for idx, doc, dist in zip(ids, documents, distances):
                    docs.append({"id": idx, "text": doc, "score": dist})
                return docs
            except Exception as e:
                print(f"Chroma query failed: {e}")
                import traceback
                traceback.print_exc()

        # memory fallback: compute cosine similarity against stored embeddings
        scored = []
        for d in self._memory_docs:
            emb = d.get("embedding")
            if emb is None:
                continue
            score = _cosine(embedding, emb)
            scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for score, d in scored[:top_k]:
            out.append({"id": d["id"], "text": d["text"], "score": float(score)})
        return out

    def list_documents(self):
        """Return a list of ingested document sources and counts, merged with file metadata."""
        print("Listing documents and merging with metadata...")
        counts = {}
        metadata_map = {}

        # 1. Get file-level metadata from meta_collection (this is our primary list of files)
        if self.meta_collection:
            try:
                res = self.meta_collection.get(include=["metadatas"])
                for md in res.get("metadatas", []):
                    if isinstance(md, dict) and "filename" in md:
                        filename = md["filename"]
                        metadata_map[filename] = md
                        # Initialize count to 0
                        counts[filename] = 0
            except Exception as e:
                print(f"Error getting file metadata: {e}")

        # 2. Get chunk counts from main collection by looking at "source" metadata
        if self.collection:
            try:
                res = self.collection.get(include=["metadatas"])
                for md in res.get("metadatas", []):
                    if isinstance(md, dict) and "source" in md:
                        src = md["source"]
                        # If we have this source, increment; otherwise ignore or add
                        counts[src] = counts.get(src, 0) + 1
            except Exception as e:
                print(f"Error getting chunk counts: {e}")

        # 3. Merge results
        # Use all unique sources found in either counts or metadata_map
        all_sources = set(counts.keys()) | set(metadata_map.keys())
        merged = []
        for src in all_sources:
            item = {
                "source": src,
                "count": counts.get(src, 0)
            }
            if src in metadata_map:
                item.update(metadata_map[src])
            merged.append(item)
        
        return merged
