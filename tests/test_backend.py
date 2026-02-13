import os
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, '.')

from fastapi.testclient import TestClient

import app.main as app_main


class BackendTests(unittest.TestCase):
    def setUp(self):
        os.environ.setdefault('ENABLE_EMBEDDING_FALLBACK', '0')
        self.client = TestClient(app_main.app)

    def test_status(self):
        r = self.client.get('/api/status')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('status', data)

    @patch('app.main.get_embeddings', return_value=[[0.0]])
    @patch('app.main.db.similarity_search_by_embedding', return_value=[])
    @patch('app.main.call_ollama_generate', return_value='TEST_ANSWER')
    def test_query_patched(self, mock_gen, mock_search, mock_emb):
        payload = {'query': 'Summarize the document', 'top_k': 2}
        r = self.client.post('/api/query', json=payload)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('answer', data)
        self.assertIn('sources', data)
        self.assertTrue('TEST_ANSWER' in data['answer'] or data['answer'] == 'TEST_ANSWER')

    def test_ingest_usecase2_md(self):
        # Use the repository's usecase2.md as a text source and upsert into the memory vector store
        from app.vectorstore import ChromaClientWrapper
        from app.ingest import chunk_text

        md_path = 'usecase2.md'
        self.assertTrue(os.path.exists(md_path), f"{md_path} not found in repo root")
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()

        chunks = chunk_text(text, chunk_size=500, overlap=100)
        # create dummy embeddings for each chunk
        emb_dim = 8
        embeddings = [[0.1] * emb_dim for _ in chunks]

        docs = []
        for i, c in enumerate(chunks):
            docs.append({
                'id': f'usecase2-{i}',
                'text': c,
                'metadata': {'source': md_path, 'chunk': i}
            })

        db = ChromaClientWrapper(persist_directory='./test_chroma')
        # upsert should use memory fallback in this environment
        db.upsert_documents(docs, embeddings=embeddings)

        items = db.list_documents()
        # find our source
        found = [it for it in items if it.get('source') == md_path]
        self.assertTrue(len(found) == 1)
        self.assertEqual(found[0]['count'], len(chunks))


if __name__ == '__main__':
    unittest.main()
