from typing import Dict, Optional

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:  # pragma: no cover
    chromadb = None


class ChromaMemory:
    def __init__(self, host: str = "chromadb", port: int = 8000):
        if chromadb is None:
            raise RuntimeError("chromadb is not installed")
        self.client = chromadb.Client(Settings(chroma_api_impl="rest", chroma_server_host=host, chroma_server_http_port=port))
        self.collection = self.client.create_collection("founderai_blueprints")

    def add_blueprint(self, blueprint_id: str, content: str, metadata: Optional[Dict] = None) -> None:
        self.collection.add(ids=[blueprint_id], documents=[content], metadatas=[metadata or {}])

    def query(self, query_text: str, n_results: int = 5):
        return self.collection.query(query_texts=[query_text], n_results=n_results)
