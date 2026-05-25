# CampusQnA 测试流程手册

## 目录

1. [前置准备](#前置准备)
2. [Docker 安装指南](#docker-安装指南)
3. [本地测试流程](#本地测试流程)
4. [云服务器部署测试流程](#云服务器部署测试流程)
5. [常见问题排查](#常见问题排查)
6. [测试检查清单](#测试检查清单)

---

## 前置准备

### 必需资源

1. **DeepSeek API Key** - 从 [DeepSeek 平台](https://platform.deepseek.com/) 获取
2. **Git 仓库访问权限** - 确保能访问 `git@github.com:VNDR-atall/CampusQnA.git`
3. **服务器** - 您的 Ubuntu 24.04 LTS 云服务器
4. **本地开发环境** - macOS / Linux / Windows

### 项目文件检查

确保您的本地项目包含以下文件：

```
CampusQnA/
├── .env                    # 环境变量配置
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 镜像配置
├── docker-compose.yml      # Docker Compose 配置
├── api/main.py             # 后端 API
├── frontend/               # Vue 3 前端
├── src/                    # RAG 核心模块
├── scripts/                # 工具脚本
├── data/                   # 文档数据
└── chroma_db/              # 向量数据库（需要先初始化）
```

---

## Docker 安装指南

### 1. 本地环境 Docker 安装

#### macOS

```bash
# 使用 Homebrew 安装 Docker Desktop
brew install --cask docker

# 启动 Docker Desktop
open -a Docker
```

或访问 [Docker 官网](https://www.docker.com/products/docker-desktop/) 下载安装。

#### Linux (Ubuntu / Debian)

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

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 验证安装
docker --version
docker compose version
```

#### Windows

访问 [Docker 官网](https://www.docker.com/products/docker-desktop/) 下载 Docker Desktop for Windows 并安装。

### 2. 云服务器 Docker 安装 (Ubuntu 24.04 LTS)

在您的云服务器上执行以下命令：

```bash
# 1. 系统更新
sudo apt update
sudo apt upgrade -y

# 2. 安装依赖
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# 3. 添加 Docker GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 4. 添加 Docker 仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 6. 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 7. 刷新用户组（或重新登录）
newgrp docker

# 8. 验证安装
docker --version
docker compose version

# 9. 启动并设置 Docker 开机自启
sudo systemctl start docker
sudo systemctl enable docker

# 10. 查看 Docker 运行状态
sudo systemctl status docker
```

### 3. Docker 常用命令速查

```bash
# 查看 Docker 版本
docker --version
docker compose version

# 查看镜像
docker images

# 查看容器
docker ps
docker ps -a  # 查看所有容器（包括停止的）

# 查看日志
docker logs <容器名>
docker logs -f <容器名>  # 实时查看日志

# 停止容器
docker stop <容器名>

# 启动容器
docker start <容器名>

# 重启容器
docker restart <容器名>

# 删除容器
docker rm <容器名>

# 删除镜像
docker rmi <镜像名>
```

---

## 本地测试流程

### 阶段 1: 本地环境准备

#### 1.1 克隆/更新项目

```bash
# 如果是首次克隆
git clone git@github.com:VNDR-atall/CampusQnA.git
cd CampusQnA

# 如果已有项目，拉取最新代码
git pull origin main
```

#### 1.2 配置环境变量

编辑 `.env` 文件：

```env
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5
CHROMA_DB_PATH=./chroma_db
DATA_DIR=./data
```

**重要**: 替换 `sk-your-actual-api-key-here` 为您的真实 DeepSeek API Key。

#### 1.3 初始化向量数据库

```bash
# 激活虚拟环境
source .cps_rag_venv/bin/activate

# 如果虚拟环境不存在，创建一个
python3 -m venv .cps_rag_venv
source .cps_rag_venv/bin/activate
pip install -r requirements.txt

# 初始化向量数据库
python scripts/init_vector_db.py
```

预期输出：
```
Loaded: ./data/...
Loaded 73 documents
Created 5494 chunks
Embedding 5494 chunks...
Loading embedding model: BAAI/bge-small-zh-v1.5
Embedding model loaded successfully
Adding 5494 documents to vector store in batches...
Added 5000/5494 documents
Added 5494/5494 documents
Documents added successfully
Vector database initialized successfully. Total chunks: 5494
```

#### 1.4 构建前端

```bash
cd frontend

# 首次安装依赖
npm install

# 构建生产版本
npm run build

cd ..
```

预期输出：
```
vite v5.x.x building for production...
✓ built in X.XXs
```

### 阶段 2: 本地非 Docker 测试

在使用 Docker 之前，先用常规方式测试确保代码正常：

```bash
# 激活虚拟环境
source .cps_rag_venv/bin/activate

# 启动 FastAPI 服务
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

打开浏览器访问：
- 主页: http://localhost:8000
- API 文档: http://localhost:8000/docs

**测试项目：**
1. [ ] 页面能正常加载
2. [ ] 快捷问题点击有反应
3. [ ] 输入问题能正常回答
4. [ ] 回答中显示来源引用
5. [ ] 加载动画正常显示

### 阶段 3: 本地 Docker 测试

#### 3.1 构建并启动 Docker 容器

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f
```

#### 3.2 查看容器状态

```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a
```

预期输出：
```
CONTAINER ID   IMAGE              COMMAND                  CREATED         STATUS         PORTS                    NAMES
abc123...      campus-qna   "uvicorn api.main:ap…"   5 seconds ago   Up 3 seconds   0.0.0.0:8000->8000/tcp   campus-qna
```

#### 3.3 访问应用

打开浏览器访问：http://localhost:8000

#### 3.4 测试 API

使用 Swagger UI 测试：
1. 访问 http://localhost:8000/docs
2. 点击 `/api/query` 接口 -> "Try it out"
3. 输入测试问题：
   ```json
   {
     "question": "计算机学院有哪些专业？"
   }
   ```
4. 点击 "Execute"，查看响应

#### 3.5 清理（可选）

```bash
# 停止容器
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 仅删除镜像
docker rmi campus-qna
```

### 阶段 4: 本地与云服务器的桥梁 - Docker 镜像传输

#### 方式 A: 通过 Git 同步（推荐）

这种方式最简单，两边都从 Git 拉取代码然后各自构建：

```bash
# 本地：提交代码
git add .
git commit -m "feat: 准备部署到服务器"
git push origin main

# 云服务器：拉取代码
git pull origin main
```

#### 方式 B: 保存和加载 Docker 镜像

如果您想在本地构建好镜像再传输到服务器：

```bash
# 本地：保存镜像
docker save campus-qna:latest | gzip > campus-qna.tar.gz

# 传输到服务器（使用 scp）
scp campus-qna.tar.gz user@your-server-ip:/path/to/destination/

# 服务器：加载镜像
ssh user@your-server-ip
cd /path/to/destination
docker load < campus-qna.tar.gz
```

#### 方式 C: 使用 Docker Hub（需要账号）

```bash
# 本地：构建并推送
docker tag campus-qna:latest your-dockerhub-username/campus-qna:latest
docker login
docker push your-dockerhub-username/campus-qna:latest

# 服务器：拉取
docker pull your-dockerhub-username/campus-qna:latest
```

---

## 云服务器部署测试流程

### 阶段 1: 云服务器准备

#### 1.1 连接到云服务器

```bash
ssh user@your-server-ip

# 或者使用您的连接方式
```

#### 1.2 安装 Docker（如果未安装）

按照上面的 [Docker 安装指南](#docker-安装指南) 在服务器上安装 Docker。

#### 1.3 克隆项目

```bash
# 首次克隆
cd ~
git clone git@github.com:VNDR-atall/CampusQnA.git
cd CampusQnA

# 或者更新已有项目
git pull origin main
```

#### 1.4 配置环境变量

```bash
nano .env
```

填入与本地相同的配置（特别是 API Key）：

```env
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5
CHROMA_DB_PATH=./chroma_db
DATA_DIR=./data
```

保存退出：`Ctrl+O` -> `Enter` -> `Ctrl+X`

### 阶段 2: 服务器上初始化向量数据库

```bash
# 创建虚拟环境
python3 -m venv .cps_rag_venv
source .cps_rag_venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化向量数据库
python scripts/init_vector_db.py
```

**重要**: 这一步会下载 Embedding 模型，确保服务器有足够的磁盘空间（约 400MB）。

### 阶段 3: 服务器上构建前端

```bash
# 安装 Node.js 和 npm（如果未安装）
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
node --version
npm --version

# 构建前端
cd frontend
npm install
npm run build
cd ..
```

### 阶段 4: 服务器上 Docker 部署

#### 4.1 启动 Docker 容器

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f
```

预期日志输出：
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
正在初始化 RAG 系统...
Loading embedding model: BAAI/bge-small-zh-v1.5
Embedding model loaded successfully
RAG 系统初始化完成！向量数据库中包含 5494 个文档块
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 4.2 配置防火墙

```bash
# 检查防火墙状态
sudo ufw status

# 如果防火墙是激活状态，允许 8000 端口
sudo ufw allow 8000

# 再次检查状态
sudo ufw status
```

如果使用云服务商（阿里云、腾讯云等），还需要在**云控制台**的安全组中开放 8000 端口。

#### 4.3 云服务安全组配置示例

**阿里云**:
1. 进入 ECS 实例 -> 安全组
2. 选择对应的安全组 -> 配置规则
3. 添加安全组规则：
   - 端口范围: 8000
   - 授权对象: 0.0.0.0/0（或指定您的 IP）

**腾讯云**:
1. 进入云服务器 -> 安全组
2. 选择安全组 -> 修改规则
3. 添加规则：
   - 协议端口: TCP:8000
   - 来源: 0.0.0.0/0

### 阶段 5: 服务器访问测试

#### 5.1 从本地浏览器访问

打开浏览器访问：
```
http://your-server-ip:8000
```

例如：
```
http://123.45.67.89:8000
```

#### 5.2 功能测试

在浏览器中进行以下测试：

| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|
| 1 | 页面加载 | 正常显示聊天界面 |
| 2 | 快捷问题 | 点击快捷问题自动发送 |
| 3 | 问答功能 | 输入问题能收到回答 |
| 4 | 来源引用 | 回答下方显示来源文档 |
| 5 | 加载动画 | 等待回答时显示加载动画 |

#### 5.3 API 测试

访问 Swagger UI：
```
http://your-server-ip:8000/docs
```

测试 `/api/query` 接口：

```json
{
  "question": "计算机学院有哪些专业？"
}
```

### 阶段 6: 服务器日志监控

```bash
# 查看实时日志
docker-compose logs -f

# 查看最后 100 行
docker-compose logs --tail=100

# 查看特定时间段
docker-compose logs --since="2026-05-19T00:00:00"
```

---

## 常见问题排查

### 问题 1: Docker 容器无法启动

**症状**: `docker-compose up` 后容器立即退出

**排查步骤**:
```bash
# 1. 查看日志
docker-compose logs

# 2. 检查端口是否被占用
sudo lsof -i :8000
# 或
sudo netstat -tulpn | grep 8000

# 3. 检查 .env 文件是否存在且配置正确
ls -la .env
cat .env

# 4. 检查向量数据库是否存在
ls -la chroma_db/
```

**解决方案**:
- 如果端口被占用：修改 `docker-compose.yml` 中的端口映射
- 如果 .env 缺少：复制并配置
- 如果向量数据库不存在：运行 `python scripts/init_vector_db.py`

### 问题 2: 前端页面 404

**症状**: 访问 http://your-server-ip:8000 显示 404

**原因**: 前端未正确构建或挂载

**解决方案**:
```bash
# 1. 检查前端构建目录
ls -la frontend/dist/

# 2. 如果 dist 目录不存在，重新构建
cd frontend
npm install
npm run build
cd ..

# 3. 重启容器
docker-compose down
docker-compose up -d --build
```

### 问题 3: API 返回错误

**症状**: 点击发送后提示错误

**排查步骤**:
```bash
# 1. 查看后端日志
docker-compose logs

# 2. 检查 DeepSeek API Key 是否正确
grep DEEPSEEK_API_KEY .env

# 3. 测试 DeepSeek API 是否正常
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### 问题 4: 向量检索返回"暂无资料"

**原因**: 向量数据库未正确初始化

**解决方案**:
```bash
# 1. 停止容器
docker-compose down

# 2. 激活虚拟环境
source .cps_rag_venv/bin/activate

# 3. 重新初始化向量数据库
python scripts/init_vector_db.py

# 4. 重启容器
docker-compose up -d
```

### 问题 5: 服务器无法访问

**症状**: 本地浏览器无法访问服务器地址

**排查步骤**:
1. [ ] 确认云服务器安全组已开放 8000 端口
2. [ ] 确认服务器防火墙已开放 8000 端口
3. [ ] 确认 Docker 容器正在运行
4. [ ] 确认服务器 IP 地址正确
5. [ ] 尝试使用 `curl` 从外部测试：
   ```bash
   curl http://your-server-ip:8000/health
   ```

---

## 测试检查清单

### 本地开发环境检查

- [ ] Python 3.10+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] `requirements.txt` 依赖已安装
- [ ] `.env` 文件已配置 API Key
- [ ] 向量数据库已初始化
- [ ] 前端已构建 (`frontend/dist/` 存在)

### Docker 环境检查

- [ ] Docker Engine 已安装
- [ ] Docker Compose Plugin 已安装
- [ ] 用户已加入 docker 组
- [ ] Docker 服务正在运行

### 本地测试检查

- [ ] `uvicorn api.main:app` 能正常启动
- [ ] http://localhost:8000 能正常访问
- [ ] 问答功能正常工作
- [ ] `docker-compose up -d --build` 成功
- [ ] Docker 容器运行正常
- [ ] Docker 容器内应用正常工作

### 云服务器检查

- [ ] 能通过 SSH 连接服务器
- [ ] 服务器上已安装 Docker
- [ ] 项目代码已克隆到服务器
- [ ] 服务器上 .env 文件已配置
- [ ] 服务器上向量数据库已初始化
- [ ] 服务器上前端已构建
- [ ] 云服务商安全组已开放 8000 端口
- [ ] 服务器防火墙已开放 8000 端口
- [ ] Docker 容器已启动
- [ ] 从公网能访问 http://your-server-ip:8000
- [ ] 问答功能在公网环境正常工作

### 功能测试检查

- [ ] 页面加载正常
- [ ] 快捷问题按钮工作
- [ ] 发送问题后有回复
- [ ] 回复包含来源引用
- [ ] 加载动画正常显示
- [ ] API 文档页面可访问
- [ ] Swagger UI 接口测试通过

---

## 维护和更新流程

### 更新代码后的重新部署

```bash
# 1. 本地：提交并推送代码
git add .
git commit -m "update: 代码更新"
git push origin main

# 2. 服务器：拉取代码
ssh user@your-server-ip
cd CampusQnA
git pull origin main

# 3. 服务器：重新初始化向量数据库（如需要）
source .cps_rag_venv/bin/activate
python scripts/init_vector_db.py

# 4. 服务器：重新构建前端（如需要）
cd frontend
npm run build
cd ..

# 5. 服务器：重启 Docker 容器
docker-compose down
docker-compose up -d --build

# 6. 服务器：查看日志
docker-compose logs -f
```

### 定期备份数据

```bash
# 备份向量数据库
tar -czf chroma_db_backup_$(date +%Y%m%d).tar.gz chroma_db/

# 备份数据文档
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/
```

---

## 快速参考命令

### 本地开发日常命令

```bash
# 进入项目目录
cd ~/CampusQnA

# 激活虚拟环境
source .cps_rag_venv/bin/activate

# 启动开发服务
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 初始化向量数据库
python scripts/init_vector_db.py

# 前端开发（热重载）
cd frontend
npm run dev
```

### Docker 日常命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 重新构建
docker-compose up -d --build
```

### 服务器日常命令

```bash
# 连接服务器
ssh user@your-server-ip

# 进入项目目录
cd ~/CampusQnA

# 更新代码
git pull origin main

# 查看容器状态
docker ps

# 查看服务健康状态
curl http://localhost:8000/health
```

---

*文档版本: v1.0*
*最后更新: 2026-05-19*
