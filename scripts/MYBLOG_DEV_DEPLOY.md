# myblog Mac 本地开发与云服务器部署手册

> **适用场景**：在 Mac 上开发 myblog → 本地 Docker/Flask 测试 → 测试通过后部署到华为云 ECS（`vndr-atall.com`）。  
> **核心原则**：代码通过 Git 同步；文章/图片/数据库在本地与生产**严格分离**，互不覆盖。

---

## 目录

1. [路径与架构速览](#1-路径与架构速览)
2. [前置要求](#2-前置要求)
3. [仓库克隆与同步策略](#3-仓库克隆与同步策略)
4. [本地环境配置](#4-本地环境配置)
5. [本地开发方式](#5-本地开发方式)
6. [本地测试清单](#6-本地测试清单)
7. [Git 工作流](#7-git-工作流)
8. [云服务器部署](#8-云服务器部署)
9. [数据分离与备份规则](#9-数据分离与备份规则)
10. [与 CampusQnA 同域说明](#10-与-campusqna-同域说明)
11. [故障排查](#11-故障排查)
12. [命令速查表](#12-命令速查表)

---

## 1. 路径与架构速览

### 1.1 实际路径（已核实）

| 环境 | 项目路径 | Git 远程 | 说明 |
|------|----------|----------|------|
| **Mac 本地（主）** | `/Users/vd/projects/myblog` | `https://github.com/VNDR-atall/myblog.git` | 日常开发目录 |
| Mac 其他副本 | `/Users/vd/.trae-cn/worktrees/myblog` | 同上 | Git worktree，非主开发目录 |
| **云服务器 ECS** | `/root/myblog` | `git@github.com:VNDR-atall/myblog.git` | 生产部署目录 |
| CampusQnA（参考） | `/Users/vd/CampusQnA` | `git@github.com:VNDR-atall/CampusQnA.git` | 同域子路径 `/campus-qna/` |

> **注意**：`~/myblog`、`/Users/vd/myblog` 在本机**不存在**；请以 `/Users/vd/projects/myblog` 为准。

### 1.2 生产架构（2026-05-27 Docker 迁移后）

```
浏览器
  └─ HTTPS vndr-atall.com (Nginx 宿主机)
       ├─ /              → 127.0.0.1:5000  (Docker: vndr-blog / myblog)
       ├─ /static/       → /root/myblog/app/static/ (Nginx 直出)
       └─ /campus-qna/   → 127.0.0.1:8000  (CampusQnA，后续集成)
```

| 组件 | 容器/进程 | 端口 | 内存限制 |
|------|-----------|------|----------|
| myblog | `vndr-blog` | `127.0.0.1:5000` | 384M |
| CampusQnA | `campus-qna` | `127.0.0.1:8000` | 1200M |
| Nginx | 宿主机 systemd | 80/443 | ~64M |

旧版 `myblog.service`（Gunicorn :8000）已 **stop + disable**，紧急回滚见 [§11.4](#114-紧急回滚到-systemd)。

### 1.3 数据存储模型

文章采用**双存储**：

| 类型 | 路径 | 内容 |
|------|------|------|
| SQLite 元数据 | `instance/app.db`（生产）/ `instance/test.db`（开发） | 标题、slug、文件夹、评论等 |
| Markdown 正文 | `content/posts/*.md` | 文章实际内容 |
| 上传图片 | `app/static/images/` | 文章图片、用户头像 |

---

## 2. 前置要求

### 2.1 Mac 本地

| 工具 | 用途 | 验证命令 |
|------|------|----------|
| **Docker Desktop** | 本地 Docker 开发/模拟生产 | `docker --version`、`docker compose version` |
| **Git** | 代码同步 | `git --version` |
| **Python 3.11+** | 非 Docker 本地开发（可选） | `python3 --version` |
| **SSH** | 登录 ECS、Git SSH（服务器侧） | `ssh -V` |

### 2.2 SSH 连接服务器

```bash
ssh root@113.45.202.80
# 域名：vndr-atall.com
```

首次连接建议验证：

```bash
ssh -T git@github.com          # Mac 若用 SSH 拉代码
ssh root@113.45.202.80 'hostname && docker ps'
```

### 2.3 端口占用须知

| 服务 | 本地端口 | 生产端口 |
|------|----------|----------|
| myblog | **5000** | `127.0.0.1:5000`（Nginx 反代） |
| CampusQnA | **8000** | `127.0.0.1:8000` |

**不要混淆**：myblog 始终是 **5000**；CampusQnA 是 **8000**。

---

## 3. 仓库克隆与同步策略

### 3.0 三方关系总览（Git / Mac / 服务器）

**唯一原则：Git 管代码，各环境各自管数据，服务器不手改 tracked 文件。**

```
                    ┌─────────────────────────────────────┐
                    │         GitHub (origin/master)       │
                    │  代码、模板、Docker 配置、脚本、文档   │
                    │  ❌ 不含：文章、图片、数据库、.env      │
                    └──────────────┬──────────────────────┘
                                   │
              git push             │             git pull
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
         ┌────────────────────┐       ┌────────────────────┐
         │  Mac 本地开发        │       │  ECS 生产服务器      │
         │  /Users/vd/projects/ │       │  /root/myblog        │
         │  myblog              │       │                      │
         ├────────────────────┤       ├────────────────────┤
         │ 数据：test.db       │       │ 数据：app.db         │
         │ 测试文章、测试图片   │       │ 正式文章、正式图片   │
         │ .env（本地密钥）    │       │ .env（生产密钥）     │
         ├────────────────────┤       ├────────────────────┤
         │ compose 选用：      │       │ compose 固定：       │
         │ · dev.yml（开发）   │       │ · prod.yml（生产）   │
         │ · yml（类生产模拟） │       │                      │
         └────────────────────┘       └────────────────────┘
```

| 层级 | 职责 | 同步方式 |
|------|------|----------|
| **Git 仓库** | 应用代码 + 三套 compose + entrypoint + 迁移脚本 | `git push` / `git pull` |
| **Mac 本地** | 开发与测试；数据与生产隔离 | 从 Git 拉代码；数据不进 Git |
| **ECS 服务器** | 对外提供服务；只跑生产数据 | 从 Git 拉代码；**禁止**在服务器上改 tracked 文件 |

#### Docker Compose 分工（均在 Git 中，按环境选用）

| 文件 | 使用环境 | 数据挂载 | 端口 |
|------|----------|----------|------|
| `docker-compose.dev.yml` | Mac 开发 | 命名卷 `_dev` + 代码 bind | `5000` |
| `docker-compose.yml` | Mac 类生产模拟 | 命名卷 `vndr_blog_*` | `5000` |
| `docker-compose.prod.yml` | **ECS 生产** | 宿主机目录 bind（`./content/posts` 等） | `127.0.0.1:5000` |

#### 服务器 `git status` 应是什么样

部署整理后，服务器上理想状态：

```bash
cd /root/myblog && git status
# On branch master
# Your branch is up to date with 'origin/master'.
# nothing to commit, working tree clean
```

若出现 `modified: docker-compose.yml` 等，说明有人在服务器上手改了 tracked 文件——应把改动合回 Git，然后 `git restore` 恢复干净工作区。

`instance/`、`content/posts/` 等数据目录即使存在也不应提交（`.gitignore` 已排除）。

### 3.1 首次克隆（Mac）

```bash
git clone https://github.com/VNDR-atall/myblog.git /Users/vd/projects/myblog
cd /Users/vd/projects/myblog
```

### 3.2 保持 Mac / 服务器代码一致

```
[Mac 开发] ──git push──► GitHub ◄──git pull── [ECS /root/myblog]
                              │
                              └── 两边 checkout 同一 commit；compose 文件按环境选用
```

| 规则 | 说明 |
|------|------|
| **只同步代码** | `.py`、模板、静态资源、Docker 配置、脚本等 |
| **不同步数据** | `content/posts/*.md`、`instance/*.db`、`app/static/images/*` 不进 Git（见 `.gitignore`） |
| **不同步密钥** | `.env` 各环境各自维护，不进 Git |
| **主分支** | `master`（非 `main`） |
| **服务器不手改** | 生产差异写在 `docker-compose.prod.yml`，不在服务器改 `docker-compose.yml` |
| **功能对等** | 同一套代码；差异仅在测试数据 vs 生产数据、compose 选用 |

### 3.3 部署前同步检查

```bash
# Mac：确认已推送
cd /Users/vd/projects/myblog
git status
git log origin/master..HEAD   # 应为空（无未推送提交）

# 服务器：确认可拉取
ssh root@113.45.202.80 'cd /root/myblog && git fetch && git log HEAD..origin/master --oneline'
```

---

## 4. 本地环境配置

### 4.1 环境变量（`.env`）

`.env` 已被 `.gitignore` 忽略，需各自维护：

**Mac 本地示例**（可选，Docker 开发 compose 已内置 dev 值）：

```env
SECRET_KEY=dev-secret-key-only-for-local-use
ADMIN_USERNAME=adminVD
ADMIN_PASSWORD=你的本地测试密码
```

**服务器 `/root/myblog/.env`**（生产，勿提交 Git）：

```env
SECRET_KEY=强随机密钥
ADMIN_USERNAME=adminVD
ADMIN_PASSWORD=强密码
```

### 4.2 FLASK_ENV 与数据库选择

由 `config.py` + `app/__init__.py` 控制：

| FLASK_ENV | 配置文件 | 数据库文件 | 场景 |
|-----------|----------|------------|------|
| `development`（默认） | `DevelopmentConfig` | `instance/test.db` | Mac 本地开发 |
| `production` | `ProductionConfig` | `instance/app.db` | Docker 生产 / 服务器 |

```python
# config.py 关键逻辑
# development → sqlite:///.../instance/test.db
# production  → sqlite:///.../instance/app.db
```

### 4.3 初始化测试数据

**方式 A：空库启动（start.sh local）**

```bash
cd /Users/vd/projects/myblog
bash start.sh local
# 内部执行 init_db.py，创建表结构
```

**方式 B：带示例数据的测试库**

```bash
cd /Users/vd/projects/myblog
source .venv/bin/activate   # 若已有虚拟环境
python init_test_db.py      # 生成测试文件夹、文章、评论
python run.py
```

当前 Mac 实测数据：

- 测试库：`/Users/vd/projects/myblog/instance/test.db`
- 测试文章：`content/posts/test*.md`、`welcome.md` 等（已被 gitignore，仅本地存在）

### 4.4 本地 vs 生产数据对照

| 数据 | Mac 本地 | 云服务器 |
|------|----------|----------|
| 数据库 | `instance/test.db` | `instance/app.db` |
| 文章 | 测试 Markdown（test1.md 等） | 正式文章（ai.md、devops.md 等） |
| Docker 卷（若用 compose） | `vndr_blog_*_dev` | 宿主机目录绑定（见下） |

---

## 5. 本地开发方式

项目提供 `start.sh` 统一入口：

```bash
bash start.sh [local|local-docker|docker|docker-detached|docker-down|docker-dev|docker-dev-down]
```

### 5.1 方式一：纯 Python（最快迭代）

```bash
cd /Users/vd/projects/myblog
bash start.sh local
```

- 自动创建 `.venv`、安装依赖、`init_db.py`
- 启动 `python run.py`（`debug=True`）
- 访问：**http://localhost:5000**
- 使用 `instance/test.db`（`FLASK_ENV` 默认 development）

### 5.2 方式二：Docker 本地开发（推荐，接近生产）

```bash
cd /Users/vd/projects/myblog
bash start.sh local-docker
# 等价于：docker compose -f docker-compose.dev.yml up --build
```

**`docker-compose.dev.yml` 行为**：

| 配置项 | 值 |
|--------|-----|
| 容器名 | `vndr-blog-dev` |
| 端口 | `5000:5000` |
| 代码挂载 | `.:/app`（**支持热重载**） |
| 数据卷 | `vndr_blog_posts_dev`、`vndr_blog_images_dev`、`vndr_blog_db_dev` |
| 环境 | `FLASK_ENV=development`、`FLASK_DEBUG=1` |
| 启动命令 | `python run.py`（entrypoint 内） |

停止开发容器：

```bash
bash start.sh docker-dev-down
# 等价于：docker compose -f docker-compose.dev.yml down
```

### 5.3 方式三：本地模拟生产 Docker

```bash
bash start.sh docker-detached   # 后台
bash start.sh docker-down       # 停止
```

使用 `docker-compose.yml`（命名卷 `vndr_blog_posts` 等，`FLASK_ENV=production`，Gunicorn 4 workers）。

### 5.4 热重载说明

| 模式 | 代码变更 | 依赖变更（requirements.txt） |
|------|----------|------------------------------|
| `start.sh local` | Flask debug 自动重载 | 需手动 `pip install -r requirements.txt` 并重启 |
| `start.sh local-docker` | 挂载 `.:/app`，改 `.py`/模板后 Flask 自动重载 | 需 `docker compose -f docker-compose.dev.yml up --build` |
| 生产 Docker | 需重新 `build` | 需重新 `build` |

---

## 6. 本地测试清单

测试通过后再 push / 部署。详细步骤亦见 myblog 仓库内 `TESTING.md`。

### 6.1 基础连通

- [ ] 首页可打开：http://localhost:5000
- [ ] 静态资源正常（CSS、图片）
- [ ] 无 500 错误（查看终端或 `docker compose logs`）

### 6.2 核心页面

| 项目 | URL | 预期 |
|------|-----|------|
| 首页 | `/` | 文件夹树、文章列表 |
| 管理员登录 | `/admin/login` 或 `/login` | 可登录 |
| 新建文章 | `/new` | 需管理员 |
| 文件管理 | `/file-manager` | 文件夹 CRUD |
| 注册/用户 | `/register`、`/user/profile` | 普通用户流程 |

默认管理员（可被 `.env` 覆盖）：用户名 `adminVD`。

### 6.3 API 测试

```bash
# 完整文件夹树（公开 API）
curl -s http://localhost:5000/api/full-folder-tree | python3 -m json.tool

# 管理员文件夹树（需登录 session，浏览器 DevTools 更直观）
# GET /api/folder-tree
```

预期：`/api/full-folder-tree` 返回 JSON，`success: true`，含 `tree` 与 `orphan_posts`。

### 6.4 新功能测试模板

1. 在功能分支或本地直接改代码
2. `bash start.sh local-docker` 或 `bash start.sh local`
3. 验证：**Happy path** + **权限边界**（未登录/admin）+ **数据持久化**（重启容器后仍在）
4. 若改 `models.py`：本地跑 `python init_db.py` 验证表结构
5. 若改 Docker/entrypoint：本地用 `docker compose -f docker-compose.dev.yml up --build` 验证

### 6.5 部署前最终确认

- [ ] 本地功能与 UI 符合预期
- [ ] `git diff` 仅包含**代码**变更，无 `.db`、无生产 `content/posts`
- [ ] 已 `git push origin master`

---

## 7. Git 工作流

### 7.1 日常开发流程

```bash
cd /Users/vd/projects/myblog

# 1. 拉最新代码
git pull origin master

# 2. 开发 & 本地测试（见 §5、§6）
bash start.sh local-docker

# 3. 仅添加代码文件（勿 add 数据）
git add app/ templates/ docker-compose*.yml Dockerfile docker-entrypoint.sh start.sh
git status   # 确认无 instance/*.db、content/posts/*.md

# 4. 提交并推送
git commit -m "feat: 描述你的改动"
git push origin master
```

### 7.2 不要提交的内容

以下已在 `.gitignore` 中，**切勿强制 add**：

```
instance/           # 所有数据库
*.db
content/posts/*.md  # 文章正文
app/static/images/* # 上传图片
.env
```

### 7.3 分支建议

当前仓库主分支为 `master`。小改动可直接在 `master` 上开发；较大功能可：

```bash
git checkout -b feature/xxx
# 开发完成后 merge 或 PR 到 master，再 push
```

---

## 8. 云服务器部署

### 8.1 服务器 Docker 配置要点

生产使用 **`docker-compose.prod.yml`**（已纳入 Git，Mac 与服务器共用同一文件）：

- 容器名：`vndr-blog`
- 端口：`127.0.0.1:5000:5000`（仅本机，由 Nginx 对外）
- **数据为宿主机目录绑定**（非命名卷）：
  - `./content/posts` → `/app/content/posts`
  - `./app/static/images` → `/app/app/static/images`
  - `./instance` → `/app/instance`
- 密钥：读取 `/root/myblog/.env`（`env_file`，不进 Git）
- 环境：`FLASK_ENV=production`、`GUNICORN_WORKERS=2`
- 健康检查：`curl -f http://localhost:5000/`
- 内存：`384M`

> Mac 上的 `docker-compose.yml`（命名卷）仅用于本地类生产模拟，**不要在 ECS 上使用**。

### 8.2 标准部署步骤（代码更新）

```bash
# 1. SSH 登录
ssh root@113.45.202.80

# 2. 【推荐】部署前备份（见 §9）
cd /root/myblog
mkdir -p /root/backups/pre-deploy-$(date +%Y%m%d-%H%M%S)
cp -a instance content/posts app/static/images /root/backups/pre-deploy-$(date +%Y%m%d-%H%M%S)/

# 3. 拉取代码（工作区应为 clean，无手改 tracked 文件）
git pull origin master
git status   # 应 nothing to commit, working tree clean

# 4. 重建并启动（二选一）
docker compose -f docker-compose.prod.yml up -d --build
# 或
bash start.sh docker-prod-down && bash start.sh docker-prod-detached

# 5. 验证
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f --tail=50
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/   # 应 200
docker inspect vndr-blog --format "{{.State.Health.Status}}"     # 应 healthy
```

### 8.3 浏览器验证

- https://vndr-atall.com/ — 首页
- 管理员登录、发一篇测试文（可选，测完可删）
- https://vndr-atall.com/static/ — 静态资源

### 8.4 Nginx

配置文件：`/etc/nginx/sites-available/myblog`

```bash
nginx -t && systemctl reload nginx
```

一般**仅改 myblog 代码无需动 Nginx**；以下情况才需 reload：

- 修改 `server_name`、SSL 证书路径
- 调整 `/static/` alias 路径
- 新增 `/campus-qna/` 反代（见 §10）

### 8.5 回滚代码

```bash
cd /root/myblog
git log --oneline -5
git checkout <上一版本commit>   # 或 git revert
docker compose -f docker-compose.prod.yml up -d --build
```

数据卷/绑定目录不受 `git checkout` 影响，文章与数据库仍在。

---

## 9. 数据分离与备份规则

### 9.1 铁律：生产数据不要覆盖本地

| ❌ 禁止 | ✅ 正确做法 |
|---------|-------------|
| `scp` / `rsync` 服务器 `instance/app.db` 到 Mac 覆盖 `test.db` | 本地始终用 `test.db` + 测试文章 |
| 把生产 `content/posts` 整体覆盖本地开发目录 | 需要参考生产文章时，复制到单独目录阅读 |
| 在 Mac 上 `docker compose` 生产配置并挂载服务器数据 | 本地用 `docker-compose.dev.yml` + `_dev` 卷 |

### 9.2 部署前必须备份（服务器）

```bash
BACKUP=/root/backups/pre-deploy-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP"
cp -a /root/myblog/instance "$BACKUP/"
cp -a /root/myblog/content/posts "$BACKUP/"
cp -a /root/myblog/app/static/images "$BACKUP/"
echo "备份于 $BACKUP"
```

历史迁移备份示例：`/root/backups/migrate-docker-20260527-125540/`

### 9.3 定期备份（可选）

```bash
#  tarball 整目录关键数据
tar czf ~/blog-backups/$(date +%Y%m%d).tar.gz \
  -C /root/myblog instance content/posts app/static/images
```

### 9.4 数据恢复

```bash
cd /root/myblog
docker compose stop
cp -a /path/to/backup/instance/* instance/
cp -a /path/to/backup/posts/* content/posts/
cp -a /path/to/backup/images/* app/static/images/
docker compose up -d
```

---

## 10. 与 CampusQnA 同域说明

CampusQnA 仓库位于 `/Users/vd/CampusQnA`，计划与 myblog **同域不同路径**部署：

| 路径 | 后端 | 端口 |
|------|------|------|
| `https://vndr-atall.com/` | myblog | 5000 |
| `https://vndr-atall.com/campus-qna/` | CampusQnA | 8000 |

参考配置（CampusQnA 仓库内）：

- `deploy/nginx-vndr-atall.conf.example`
- `deploy/docker-compose.stack.yml.example`
- `docs/deployment.md` →「与 myblog 集成」

**本地开发时**：

- myblog：`http://localhost:5000`
- CampusQnA：`http://localhost:8000`（`uvicorn` 或 `docker compose up`）

两者独立进程，**不要**把 CampusQnA 配到 5000 端口。

---

## 11. 故障排查

### 11.1 Nginx 502 Bad Gateway

**原因**：`vndr-blog` 未运行或未监听 5000。

```bash
ssh root@113.45.202.80
docker compose -f /root/myblog/docker-compose.yml ps
docker compose -f /root/myblog/docker-compose.yml logs --tail=100
curl -v http://127.0.0.1:5000/
```

处理：重启容器 `docker compose up -d --build`；检查内存是否 OOM（`dmesg | tail`）。

### 11.2 首页空白 / 文章列表为空

**可能原因**：

1. `instance/app.db` 中无 post 记录
2. `content/posts/` 中 Markdown 与数据库 `filename` 不匹配
3. entrypoint 误初始化空库（见 §11.3）

```bash
# 服务器检查
ls -la /root/myblog/instance/
ls /root/myblog/content/posts/ | wc -l
docker compose -f /root/myblog/docker-compose.yml logs | grep -i "初始化\|migrate\|app.db"
```

从备份恢复 `instance/app.db`（见 §9.4）。

### 11.3 entrypoint 覆盖 / 误初始化数据库

服务器 `docker-entrypoint.sh` 会在启动时：

1. 检查 `instance/app.db` 表结构是否完整（含 `folder.parent_id`）
2. 若需初始化：尝试 `scripts/migrate_legacy_to_instance.py`（从根目录 `app.db` 迁移）
3. 否则尝试从 `instance/test.db` 恢复（若含文章）
4. 仍为空则 `init_db.py` 建空库

**风险**：空库或 schema 不匹配时可能覆盖/重建数据。

**预防**：

- 部署前备份 `instance/`（§9.2）
- 确认 `instance/app.db` 非 0 字节且含文章后再 `up --build`
- 服务器上保留 `app.db.bak-*` 备份文件

### 11.4 容器 OOM（内存不足）

ECS 为 2 GiB RAM，myblog limit 384M。若被 kill：

```bash
docker inspect vndr-blog --format '{{.State.OOMKilled}}'
# 可调低 GUNICORN_WORKERS 或 compose 中 memory limits
```

建议启用 2G swap（CampusQnA `deploy/README.md` 有说明）。

### 11.5 502 / 端口冲突

```bash
# 谁占用 5000
ss -tlnp | grep 5000
# 旧 systemd 服务是否误启动
systemctl status myblog.service
```

### 11.6 紧急回滚到 systemd

见服务器 `/root/myblog/DOCKER_MIGRATION.md`：

```bash
systemctl enable --now myblog.service
sed -i "s|127.0.0.1:5000|127.0.0.1:8000|" /etc/nginx/sites-available/myblog
nginx -t && systemctl reload nginx
cd /root/myblog && docker compose stop
```

> 仅紧急情况使用；正常路径应修复 Docker 容器。

### 11.7 Mac 本地端口被占用

```bash
lsof -i :5000
# 停止占用进程或 docker compose down
```

---

## 12. 命令速查表

### Mac 本地

| 目的 | 命令 |
|------|------|
| 进入项目 | `cd /Users/vd/projects/myblog` |
| Python 开发 | `bash start.sh local` |
| Docker 开发 | `bash start.sh local-docker` |
| 停止 Docker 开发 | `bash start.sh docker-dev-down` |
| 测试 API | `curl -s http://localhost:5000/api/full-folder-tree \| python3 -m json.tool` |
| 初始化测试数据 | `python init_test_db.py` |
| 推送代码 | `git push origin master` |

### 云服务器

| 目的 | 命令 |
|------|------|
| SSH | `ssh root@113.45.202.80` |
| 进入项目 | `cd /root/myblog` |
| 拉代码 | `git pull origin master` |
| 部署 | `docker compose -f docker-compose.prod.yml up -d --build` |
| 查看状态 | `docker compose -f docker-compose.prod.yml ps` |
| 查看日志 | `docker compose -f docker-compose.prod.yml logs -f` |
| 健康检查 | `docker inspect vndr-blog --format "{{.State.Health.Status}}"` |
| 本机探活 | `curl -I http://127.0.0.1:5000/` |
| 重载 Nginx | `nginx -t && systemctl reload nginx` |
| 部署前备份 | `cp -a instance content/posts app/static/images /root/backups/manual-$(date +%Y%m%d)/` |

### Git

| 目的 | 命令 |
|------|------|
| 状态 | `git status` |
| 未推送提交 | `git log origin/master..HEAD` |
| 拉取 | `git pull origin master` |
| 提交 | `git add <files> && git commit -m "msg" && git push origin master` |

---

## 附录：相关文件索引

| 文件 | 位置 | 说明 |
|------|------|------|
| `start.sh` | myblog 根目录 | 本地/ Docker 启动入口 |
| `docker-compose.dev.yml` | myblog 根目录 | Mac Docker 开发 |
| `docker-compose.yml` | myblog 根目录 | Mac 类生产模拟（命名卷） |
| `docker-compose.prod.yml` | myblog 根目录 | ECS 生产部署（bind mount） |
| `docker-entrypoint.sh` | myblog 根目录 | 容器启动、DB 检查与迁移 |
| `scripts/migrate_legacy_to_instance.py` | myblog 根目录 | 旧版 app.db → instance/app.db 迁移 |
| `docs/DOCKER_MIGRATION.md` | myblog 根目录 | Docker 迁移记录与回滚 |
| `DEPLOYMENT.md` | myblog 根目录 | 原项目部署文档 |
| `TESTING.md` | myblog 根目录 | 功能测试步骤 |
| `config.py` | myblog 根目录 | FLASK_ENV / 数据库 URI |
| Nginx | 服务器 `/etc/nginx/sites-available/myblog` | HTTPS 反代 |

---

*文档版本：v1.1 · 2026-05-29 整理三方关系：生产 compose 纳入 Git（`docker-compose.prod.yml`），服务器不再手改 tracked 文件。*
