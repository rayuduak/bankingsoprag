"""LLM and embeddings wrappers for Ollama (local) with a sentence-transformers fallback."""
from typing import List
import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")


def call_ollama_generate(prompt: str, model: str = "gemma3:latest", stream: bool = False):
    url = f"{OLLAMA_URL}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": stream}
    print(payload)
    if stream:
        def generator():
            with requests.post(url, json=payload, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                        if chunk.get("done"):
                            break
        return generator()
    else:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        # If it was returned as a stream of JSONs (default Ollama behavior if stream not specified or True)
        # We need to concatenate them if they came back as multiple lines
        full_response = ""
        for line in resp.text.strip().split('\n'):
            if not line: continue
            try:
                chunk = json.loads(line)
                full_response += chunk.get("response", "")
            except:
                # If it's just raw text
                full_response += line
        print(full_response)
        return full_response


def call_ollama_embeddings(texts: List[str], model: str = "gemma3:latest") -> List[List[float]]:
    if not texts:
        return []
    url = f"{OLLAMA_URL}/api/embeddings"
    payload = {"model": model, "input": texts}
    print(f"Requesting embeddings from Ollama for {len(texts)} texts...")
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    # Ensure result is always a list of lists
    embeddings = []
    
    if isinstance(data, dict):
        if "embeddings" in data:
            embeddings = data["embeddings"]
        elif "data" in data:
            # 'data' can be list of vectors or list of objects
            d = data["data"]
            if len(d) > 0 and isinstance(d[0], dict) and "embedding" in d[0]:
                embeddings = [item["embedding"] for item in d]
            else:
                embeddings = d
        elif "embedding" in data:
            embeddings = [data["embedding"]]
    elif isinstance(data, list):
        embeddings = data

    # Validation: sometimes Ollama returns a single list for a single input text
    # when a list of lists was expected. 
    if len(texts) == 1 and len(embeddings) > 0 and not isinstance(embeddings[0], list):
        embeddings = [embeddings]
        
    if not embeddings:
        raise RuntimeError(f"Could not extract embeddings from Ollama response: {data}")
        
    print(f"Successfully retrieved {len(embeddings)} vectors.")
    return embeddings


def embed_with_sentence_transformer(text: str) -> List[float]:
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise RuntimeError("sentence-transformers not available") from e

    model = SentenceTransformer("all-MiniLM-L6-v2")
    vec = model.encode([text])[0]
    return vec.tolist()


_model_cache = {}

def get_sentence_transformer_model():
    if "model" not in _model_cache:
        try:
            from sentence_transformers import SentenceTransformer
            print("Loading open-source embedding model (all-MiniLM-L6-v2)...")
            _model_cache["model"] = SentenceTransformer("all-MiniLM-L6-v2")
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading sentence-transformers: {e}")
            return None
    return _model_cache.get("model")


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings using open-source sentence-transformers (default)
    with Ollama as a fallback.
    """
    if not texts:
        return []

    # Try open-source model first as requested
    model = get_sentence_transformer_model()
    if model:
        try:
            vecs = model.encode(texts)
            return [v.tolist() for v in vecs]
        except Exception as e:
            print(f"Sentence-transformers encoding failed: {e}. Falling back to Ollama.")

    # Fallback to Ollama
    try:
        return call_ollama_embeddings(texts)
    except Exception as e:
        print(f"Ollama embedding also failed: {e}")
        raise
