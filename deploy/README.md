# vndr-atall.com ECS 部署栈

华为云 ECS：**2 vCPU / 2 GiB RAM**，Ubuntu 24.04。同域集成 [CampusQnA](../README.md) 与 [myblog](https://github.com/VNDR-atall/myblog)（路径示例 `/opt/myblog`）。

## 内存预算（约 2 GiB）

| 组件 | 建议 limit | 说明 |
|------|------------|------|
| campus-qna | 1200M | 仅此容器加载嵌入模型；Chroma 已预构建 |
| myblog (gunicorn) | 256M | Flask 轻量 |
| nginx（宿主机或容器） | ~64M | 反代 |
| 系统 + Docker | 余量 | 建议 **2G swap** |

策略：

- **chroma_db**：在开发机或服务器上执行一次 `python scripts/init_vector_db.py`，再通过 `rsync`/`scp` 同步到 ECS，**不要进 Git**。
- **data/**：PDF 放在服务器卷，不进 Git。
- 嵌入模型只在 campus-qna 进程内加载一次。

## 文件

- [`nginx-vndr-atall.conf.example`](./nginx-vndr-atall.conf.example) — Nginx：`/campus-qna/` → `127.0.0.1:8000`，`/` → `127.0.0.1:5000`
- [`docker-compose.stack.yml.example`](./docker-compose.stack.yml.example) — 双服务编排示例

## 快速步骤

1. 安装 Docker、Nginx；可选：`fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile`
2. Clone `CampusQnA`、`myblog`；配置 `.env`（DeepSeek 等）
3. 同步 `chroma_db/`、`data/` 到 `/opt/CampusQnA/`
4. `docker compose -f deploy/docker-compose.stack.yml.example up -d --build`（复制并改路径后）
5. 启用 Nginx 站点，`nginx -t && systemctl reload nginx`
6. `certbot --nginx -d vndr-atall.com`（若尚未 HTTPS）

详细说明见 [docs/deployment.md](../docs/deployment.md) 中「与 myblog 集成」。

## HTTPS 验证

```bash
curl -I https://vndr-atall.com/campus-qna/health
openssl s_client -connect vndr-atall.com:443 -servername vndr-atall.com </dev/null 2>/dev/null | openssl x509 -noout -subject -dates
```

浏览器访问：`https://vndr-atall.com/campus-qna/` 与博客首页导航「校园问答」。
