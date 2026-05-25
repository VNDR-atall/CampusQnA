from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import (
    Config,
    EmbeddingModel,
    VectorStore,
    RAGSystem
)

ROOT_PATH = os.getenv("ROOT_PATH", "/campus-qna")

app = FastAPI(
    title="CampusQnA API",
    description="校园百事通 RAG 问答系统 API",
    version="1.0.0",
    root_path=ROOT_PATH,
)

# CORS：生产同域 + 本地开发
_cors_origins = [
    "https://vndr-atall.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
_extra = os.getenv("CORS_ORIGINS", "")
if _extra:
    _cors_origins.extend(o.strip() for o in _extra.split(",") if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
rag_system: Optional[RAGSystem] = None

# Pydantic 模型
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict]
    context: List[Dict]

class HealthResponse(BaseModel):
    status: str
    version: str

# 事件处理
@app.on_event("startup")
async def startup_event():
    """服务启动时初始化"""
    global rag_system
    
    print("正在初始化 RAG 系统...")
    
    # 初始化嵌入模型
    embedding_model = EmbeddingModel.get_instance(Config.EMBEDDING_MODEL_NAME)
    
    # 初始化向量存储
    vector_store = VectorStore(Config.CHROMA_DB_PATH, embedding_model)
    vector_store.create_collection()
    
    # 初始化 RAG 系统
    rag_system = RAGSystem(vector_store)
    
    # 检查向量数据库
    stats = vector_store.get_collection_stats()
    print(f"RAG 系统初始化完成！向量数据库中包含 {stats['count']} 个文档块")

# API 路由
@app.get("/", response_class=FileResponse)
async def root():
    """根路径，返回前端页面"""
    static_path = os.path.join(os.path.dirname(__file__), '../frontend/dist/index.html')
    if os.path.exists(static_path):
        return FileResponse(static_path)
    return {"message": "CampusQnA API 服务已运行，请访问 /docs 查看文档"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse(
        status="ok",
        version="1.0.0"
    )

@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """问答接口"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG 系统未初始化")
    
    try:
        result = rag_system.query(request.question)
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            context=result["context"]
        )
    except Exception as e:
        print(f"问答失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """获取统计信息"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG 系统未初始化")
    
    stats = rag_system.vector_store.get_collection_stats()
    return {
        "collection": stats["name"],
        "document_count": stats["count"],
        "model": Config.EMBEDDING_MODEL_NAME
    }

# 挂载静态文件（前端）
static_dir = os.path.join(os.path.dirname(__file__), '../frontend/dist')
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
