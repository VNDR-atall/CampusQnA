import os
import chromadb
from chromadb.config import Settings
from typing import List, Tuple, Dict
from .embedding import EmbeddingModel

class VectorStore:
    def __init__(self, db_path: str, embedding_model: EmbeddingModel):
        self.db_path = db_path
        self.embedding_model = embedding_model
        self.client = self._init_client()
        self.collection = None
    
    def _init_client(self):
        os.makedirs(self.db_path, exist_ok=True)
        return chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(allow_reset=True)
        )
    
    def create_collection(self, collection_name: str = "campus_knowledge"):
        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception:
            self.collection = self.client.create_collection(collection_name)
    
    def delete_collection(self, collection_name: str = "campus_knowledge"):
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass
    
    def add_documents(self, chunks: List[Tuple[str, dict]], batch_size: int = 5000):
        if not self.collection:
            self.create_collection()
        
        texts = [chunk[0] for chunk in chunks]
        metadatas = [chunk[1] for chunk in chunks]
        ids = [metadata.get("chunk_id", f"chunk_{i}") for i, (_, metadata) in enumerate(chunks)]
        
        print(f"Embedding {len(texts)} chunks...")
        embeddings = self.embedding_model.encode(texts)
        
        print(f"Adding {len(ids)} documents to vector store in batches...")
        total_added = 0
        
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            
            self.collection.add(
                embeddings=batch_embeddings,
                documents=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            total_added += len(batch_ids)
            print(f"Added {total_added}/{len(ids)} documents")
        
        print("Documents added successfully")
    
    def query(self, query_text: str, top_k: int = 3) -> List[Dict]:
        if not self.collection:
            self.create_collection()
        
        query_embedding = self.embedding_model.encode_single(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return self._format_results(results)
    
    def _format_results(self, results: dict) -> List[Dict]:
        formatted = []
        
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        return formatted
    
    def get_collection_stats(self) -> dict:
        if not self.collection:
            self.create_collection()
        
        return {
            "count": self.collection.count(),
            "name": self.collection.name
        }