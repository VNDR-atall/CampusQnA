# CampusQnA - 校园百事通

基于 RAG（检索增强生成）的校园公开信息智能问答系统。

## 项目简介

CampusQnA 是一个面向高校学生的智能问答系统，通过自然语言交互方式，帮助学生快速获取学校官方发布的各类信息，如培养方案、校规校纪、办事指南等。

### 核心特性

- **文档解析**: 支持 PDF、TXT 等常见文档格式
- **智能检索**: 基于向量数据库的语义检索
- **准确回答**: 结合检索结果生成可溯源的回答
- **来源引用**: 所有回答均附带来源文档引用
- **Web 界面**: 美观的 Vue 3 聊天界面
- **快速部署**: Docker 一键部署

## 技术架构

```
┌─────────────────┐
│   前端（Vue 3）  │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   FastAPI 后端   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐
│  RAG    │ │ SQLite  │
│ Service │ │ 日志    │
└────┬────┘ └─────────┘
     │
┌────┴────┐
│ChromaDB │
│向量数据库│
└─────────┘
```

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 后端框架 | FastAPI | 异步 API 服务 |
| 前端框架 | Vue 3 + Vite | 现代前端开发 |
| 向量数据库 | ChromaDB | 嵌入式向量存储 |
| 嵌入模型 | BAAI/bge-small-zh-v1.5 | 中文文本向量化 |
| 大模型 API | DeepSeek | 回答生成 |
| PDF解析 | pdfplumber | PDF 文本提取 |
| 容器化 | Docker | 一键部署 |

## 项目结构

```
CampusQnA/
├── api/                    # FastAPI 后端
│   ├── __init__.py
│   └── main.py
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── src/                    # RAG 核心模块
│   ├── __init__.py
│   ├── config.py
│   ├── document_parser.py
│   ├── chunker.py
│   ├── embedding.py
│   ├── vector_store.py
│   └── rag.py
├── scripts/                # 工具脚本
│   ├── init_vector_db.py
│   └── chat.py
├── data/                   # 文档数据
├── chroma_db/              # 向量数据库
├── docs/                   # 文档
│   ├── git_manual.md
│   ├── deepseek_api_manual.md
│   └── deployment.md
├── .env                    # 环境变量
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- Docker（可选，推荐）

### 本地开发部署

#### 1. 配置环境变量

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5
CHROMA_DB_PATH=./chroma_db
DATA_DIR=./data
```

#### 2. 初始化向量数据库

```bash
# 激活虚拟环境
source .cps_rag_venv/bin/activate

# 初始化向量数据库
python scripts/init_vector_db.py
```

#### 3. 构建前端

```bash
cd frontend
npm install
npm run build
cd ..
```

#### 4. 启动服务

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 http://localhost:8000 即可查看应用！

### Docker 部署（推荐）

#### 1. 初始化向量数据库

```bash
source .cps_rag_venv/bin/activate
python scripts/init_vector_db.py
```

#### 2. 启动容器

```bash
docker-compose up -d --build
```

访问 http://your-server-ip:8000 即可查看应用！

## API 文档

启动后端服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要 API

| 接口 | 方法 | 说明 |
|------|------|------|
| / | GET | 前端页面 |
| /health | GET | 健康检查 |
| /api/query | POST | 问答接口 |
| /api/stats | GET | 获取统计信息 |

## 使用说明

### 问答接口示例

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "计算机学院有哪些专业？"}'
```

响应格式：

```json
{
  "answer": "根据文档，计算机学院有以下专业...",
  "sources": [
    {
      "title": "2024级计算机学院培养方案.pdf",
      "department": "2024级本科专业人才培养方案",
      "source": "./data/..."
    }
  ],
  "context": [...]
}
```

## 开发指南

### 前端开发

```bash
cd frontend
npm install
npm run dev  # 开发模式
npm run build  # 构建生产版本
```

### 后端开发

```bash
source .cps_rag_venv/bin/activate
uvicorn api.main:app --reload
```

### 提交规范

遵循语义化 commit 消息：

- `feat: 新功能`
- `fix: 修复 bug`
- `docs: 更新文档`
- `refactor: 重构`
- `test: 测试`
- `chore: 杂项`

## 与 myblog 集成

生产环境通过 **Nginx 同域子路径** 挂载：`https://vndr-atall.com/campus-qna/`（博客根站 `/` 为 myblog）。Docker 仅暴露 `127.0.0.1:8000`，向量库与 PDF 在服务器卷同步，不进 Git。

- 部署与 HTTPS 校验：[部署指南 · 与 myblog 集成](./docs/deployment.md#与-myblog-集成)
- Nginx / 全栈示例：[deploy/](./deploy/)

## 文档

- [Git 使用手册](./docs/git_manual.md)
- [DeepSeek API 手册](./docs/deepseek_api_manual.md)
- [部署指南](./docs/deployment.md)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

*项目状态: MVP 完成*
*最后更新: 2026-05-19*
