import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import Config, EmbeddingModel, VectorStore, RAGSystem

def main():
    print("Initializing RAG system...")
    
    embedding_model = EmbeddingModel.get_instance(Config.EMBEDDING_MODEL_NAME)
    vector_store = VectorStore(Config.CHROMA_DB_PATH, embedding_model)
    vector_store.create_collection()
    
    stats = vector_store.get_collection_stats()
    print(f"Vector database loaded. Total chunks: {stats['count']}")
    
    if stats["count"] == 0:
        print("No documents in vector database. Please run 'python scripts/init_vector_db.py' first.")
        return
    
    rag_system = RAGSystem(vector_store)
    
    print("\n校园百事通 - RAG问答系统")
    print("输入 'quit' 或 'exit' 退出")
    print("-" * 50)
    
    while True:
        query = input("\n请输入你的问题：")
        
        if query.lower() in ["quit", "exit"]:
            print("再见！")
            break
        
        if not query.strip():
            continue
        
        print("正在检索...")
        result = rag_system.query(query)
        
        print("\n回答：")
        print(result["answer"])
        
        if result["sources"]:
            print("\n引用来源：")
            for i, source in enumerate(result["sources"], 1):
                print(f"{i}. {source['department']}/{source['title']}")

if __name__ == "__main__":
    main()