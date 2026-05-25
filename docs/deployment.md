# CampusQnA 部署指南

## 本地开发部署

### 前置要求

- Python 3.10+
- Node.js 18+
- Docker（可选，用于 Docker 部署）

### 步骤 1: 克隆项目

```bash
git clone git@github.com:VNDR-atall/CampusQnA.git
cd CampusQnA
```

### 步骤 2: 配置环境变量

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5
CHROMA_DB_PATH=./chroma_db
DATA_DIR=./data
```

### 步骤 3: 初始化向量数据库

```bash
# 激活虚拟环境
source .cps_rag_venv/bin/activate

# 初始化向量数据库
python scripts/init_vector_db.py
```

### 步骤 4: 构建前端

```bash
cd frontend
npm install
npm run build
cd ..
```

### 步骤 5: 启动后端服务

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 http://localhost:8000 即可查看应用！

---

## Docker 部署（推荐）

### 前置要求

- Docker
- Docker Compose

### 部署步骤

#### 1. 确保向量数据库已初始化

在本地先运行向量数据库初始化：

```bash
source .cps_rag_venv/bin/activate
python scripts/init_vector_db.py
```

#### 2. 构建并启动 Docker 容器

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f
```

#### 3. 访问应用

打开浏览器访问：http://your-server-ip:8000

### Docker 常用命令

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 更新镜像并重启
docker-compose down
docker-compose up -d --build
```

---

## Ubuntu 服务器部署

### 服务器环境准备

#### 1. 安装 Docker 和 Docker Compose

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装依赖
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

#### 2. 将用户添加到 docker 组（可选，避免使用 sudo）

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 部署步骤

#### 1. 拉取代码

```bash
# 如果是首次部署
git clone git@github.com:VNDR-atall/CampusQnA.git
cd CampusQnA

# 如果是更新
git pull origin main
```

#### 2. 配置环境变量

```bash
# 复制 .env 文件并编辑
nano .env
```

填入你的 DeepSeek API Key。

#### 3. 初始化向量数据库

```bash
# 创建虚拟环境
python3 -m venv .cps_rag_venv
source .cps_rag_venv/bin/activate
pip install -r requirements.txt

# 初始化向量数据库
python scripts/init_vector_db.py
```

#### 4. 构建前端

```bash
cd frontend
npm install
npm run build
cd ..
```

#### 5. Docker 部署

```bash
# 构建并启动
docker-compose up -d --build

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 6. 配置防火墙（如需要）

```bash
# 允许 8000 端口
sudo ufw allow 8000

# 查看状态
sudo ufw status
```

---

## 与 myblog 集成

在 **vndr-atall.com** 同域下，通过 Nginx 将子路径 `/campus-qna/` 反代到 CampusQnA（`127.0.0.1:8000`），根路径 `/` 反代到 myblog（`127.0.0.1:5000`）。公开访问，无额外鉴权。

### 架构（方案 A）

```
浏览器 → Nginx (443) ─┬─ /campus-qna/* → campus-qna:8000 (Docker)
                      └─ /*            → myblog:5000 (Docker)
```

仓库内示例配置：

- [`deploy/nginx-vndr-atall.conf.example`](../deploy/nginx-vndr-atall.conf.example)
- [`deploy/docker-compose.stack.yml.example`](../deploy/docker-compose.stack.yml.example)
- [`deploy/README.md`](../deploy/README.md) — 2 GiB 内存预算与 swap 建议

### 前端与 API 路径

- Vite `base: '/campus-qna/'`
- 生产环境 `VITE_API_BASE=/campus-qna`（见 `frontend/.env.production.example`）
- FastAPI `ROOT_PATH=/campus-qna`（docker-compose 已设置）

### 数据部署（2 GiB ECS 推荐）

| 内容 | 策略 |
|------|------|
| `chroma_db/` | 本地或服务器**一次性**运行 `scripts/init_vector_db.py`，再 `rsync -avz chroma_db/ user@ecs:/opt/CampusQnA/chroma_db/` |
| `data/`（PDF） | 放在服务器目录挂载进容器，**不进 Git** |
| `.env` | 服务器单独创建，挂载只读 |

不在镜像构建时复制 `chroma_db`/`data`，避免镜像过大与 Git 泄露。

```bash
# 示例：从本机同步向量库
rsync -avz --progress ./chroma_db/ user@vndr-atall.com:/opt/CampusQnA/chroma_db/
rsync -avz --progress ./data/ user@vndr-atall.com:/opt/CampusQnA/data/
```

### 服务器操作清单

1. `git clone` CampusQnA 到例如 `/opt/CampusQnA`
2. 创建 `.env`（DeepSeek API Key 等）
3. 同步 `chroma_db/`、`data/`
4. `docker compose up -d --build`（仅绑定 `127.0.0.1:8000`）
5. myblog 同样 Docker 部署并绑定 `127.0.0.1:5000`（见 myblog `docs/integrations.md`）
6. 复制并启用 Nginx 配置，`nginx -t && systemctl reload nginx`
7. 博客导航已链到 `/campus-qna/`；可发布介绍文章（见 myblog `content/posts/campus-qna-intro.md`）

### HTTPS 验证

证书签发给域名即可覆盖子路径 `/campus-qna/`。

```bash
# 应返回 200 与 JSON（或 FastAPI 响应头）
curl -I https://vndr-atall.com/campus-qna/health

# 检查证书与 SNI
openssl s_client -connect vndr-atall.com:443 -servername vndr-atall.com </dev/null 2>/dev/null | openssl x509 -noout -subject -dates

# 问答抽测（可选）
curl -s -X POST https://vndr-atall.com/campus-qna/api/query \
  -H "Content-Type: application/json" \
  -d '{"question":"计算机学院有哪些专业？"}' | head -c 500
```

浏览器：打开 `https://vndr-atall.com/campus-qna/`，从博客首页点击「校园问答」。

### ECS 2 GiB 内存建议

- Docker limits：`campus-qna` 1200M，`myblog` 256M，nginx ~64M（见 `deploy/README.md`）
- 启用 **swap**（2G）以防 OOM
- 嵌入模型仅在 campus-qna 容器加载；避免在 ECS 上重复 `init_vector_db` 若内存紧张，改在开发机构建 chroma 后 rsync

---

## Nginx 反向代理（可选，建议生产环境使用）

### 安装 Nginx

```bash
sudo apt install -y nginx
```

### 配置 Nginx

创建配置文件：

```bash
sudo nano /etc/nginx/sites-available/campus-qna
```

填入以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/campus-qna /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL 配置（使用 Let's Encrypt）

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

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
├── .env                    # 环境变量
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 故障排查

### 问题 1: Docker 容器无法启动

检查日志：
```bash
docker-compose logs
```

确保 .env 文件配置正确，且向量数据库已初始化。

### 问题 2: API 响应错误

检查后端日志：
```bash
docker-compose logs -f
```

确保 DeepSeek API Key 有效且有余额。

### 问题 3: 前端无法访问后端

检查是否有 CORS 问题，确认 Nginx 配置正确（如使用了反向代理）。

---

## 更新文档

### 更新项目代码

```bash
git pull origin main
```

### 重新部署

```bash
# 停止旧容器
docker-compose down

# 重新初始化向量数据库（如需要）
source .cps_rag_venv/bin/activate
python scripts/init_vector_db.py

# 重新构建前端
cd frontend
npm run build
cd ..

# 启动新容器
docker-compose up -d --build
```

---

*文档版本: v1.0*
*最后更新: 2026-05-19*
