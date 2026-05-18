import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import Config, DocumentParser, TextChunker, EmbeddingModel, VectorStore

def main():
    print("Initializing vector database...")
    
    documents = DocumentParser.load_documents(Config.DATA_DIR)
    print(f"Loaded {len(documents)} documents")
    
    if not documents:
        print("No documents found. Exiting.")
        return
    
    chunker = TextChunker(chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP)
    chunks = chunker.chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")
    
    embedding_model = EmbeddingModel.get_instance(Config.EMBEDDING_MODEL_NAME)
    
    vector_store = VectorStore(Config.CHROMA_DB_PATH, embedding_model)
    vector_store.delete_collection()
    vector_store.create_collection()
    
    vector_store.add_documents(chunks)
    
    stats = vector_store.get_collection_stats()
    print(f"Vector database initialized successfully. Total chunks: {stats['count']}")

if __name__ == "__main__":
    main()