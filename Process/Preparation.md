## 建立项目并初始化

```bash
mkdir CampusQnA
cd CampusQnA
python -m venv .cps_rag_venv

git init
```

## 创建.gitignore
```gitignore
# Python
__pycache__/
*.pyc

# venv
.cps_rag_venv/

# macOS
.DS_Store

# ChromaDB
chroma_db/

# env
.env

# IDE
.vscode/
.idea/

# logs
logs/

# model cache
hf_cache/
```

## 上传 github 仓库
### 1. 在仓库中建立CampusQnA
### 2. 若没有SSH密钥，考虑新建一个
1. 生成密钥
```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 或者使用 RSA（如果系统不支持 ed25519）
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

2. 添加SSH密钥到SSH代理
```bash
# 启动 ssh-agent
eval "$(ssh-agent -s)"

# 添加私钥到 ssh-agent
ssh-add ~/.ssh/id_ed25519
```

3. 添加公钥到 GitHub
```bash
# 复制公钥内容
cat ~/.ssh/id_ed25519.pub
# 然后登录 GitHub → Settings → SSH and GPG keys
# 点击 "New SSH key"  
# 粘贴公钥内容，保存
```

4. 测试SSH连接
```bash
ssh -T git@github.com
# 成功会显示：Hi username! You've successfully authenticated...
```

### 3. 添加远程仓库
```bash
git remote add origin git@github.com:VNDR-atall/CampusQnA.git
```

### 4. 添加所有文件到暂存区
```bash
git add .
```

### 5. 提交到本地仓库
```bash
git commit -m "git init; test data ready"
```

