# CampusQnA Git 使用手册

## 一、仓库信息

- **仓库地址**: `git@github.com:VNDR-atall/CampusQnA.git`
- **默认分支**: `main`
- **用户配置**: 
  - 用户名: VNDR
  - 邮箱: 15986655215@163.com

## 二、常用 Git 命令

### 1. 克隆仓库
```bash
git clone git@github.com:VNDR-atall/CampusQnA.git
cd CampusQnA
```

### 2. 查看状态
```bash
git status
```

### 3. 添加文件到暂存区
```bash
git add .                    # 添加所有修改
git add src/rag.py           # 添加指定文件
```

### 4. 提交修改
```bash
git commit -m "feat: 添加RAG检索模块"   # 直接提交
git commit -a -m "fix: 修复PDF解析bug"   # 添加并提交所有已跟踪文件
```

### 5. 拉取远程更新
```bash
git pull origin main         # 拉取主分支更新
```

### 6. 推送本地提交
```bash
git push origin main         # 推送到主分支
```

### 7. 创建分支
```bash
git checkout -b feature/rag-api   # 创建并切换到新分支
```

### 8. 切换分支
```bash
git checkout main            # 切换到主分支
git checkout feature/rag-api # 切换到特性分支
```

### 9. 查看分支
```bash
git branch                   # 查看本地分支
git branch -a                # 查看所有分支（包括远程）
```

### 10. 合并分支
```bash
git checkout main            # 先切换到目标分支
git merge feature/rag-api    # 合并特性分支到主分支
```

### 11. 删除分支
```bash
git branch -d feature/rag-api    # 删除本地分支
git push origin --delete feature/rag-api  # 删除远程分支
```

### 12. 查看提交历史
```bash
git log                      # 查看完整提交历史
git log --oneline            # 简洁格式查看
git log --oneline -10        # 查看最近10次提交
```

### 13. 撤销修改
```bash
git checkout -- src/rag.py   # 撤销工作区修改
git reset HEAD src/rag.py    # 撤销暂存区修改
```

## 三、工作流规范

### 1. 日常开发流程

```
1. 拉取最新代码
   git pull origin main

2. 创建特性分支
   git checkout -b feature/xxx

3. 开发代码...

4. 提交修改
   git add .
   git commit -m "feat: 描述你的修改"

5. 推送分支到远程
   git push origin feature/xxx

6. 创建 Pull Request（在GitHub网页上）

7. 代码审查通过后合并到main
```

### 2. Commit 消息规范

使用统一的 commit 消息格式：

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加文档解析模块` |
| `fix` | 修复bug | `fix: 修复PDF乱码问题` |
| `docs` | 更新文档 | `docs: 更新API手册` |
| `refactor` | 代码重构 | `refactor: 优化Chunk切分逻辑` |
| `test` | 添加测试 | `test: 添加向量检索测试` |
| `chore` | 杂务（配置、依赖等） | `chore: 更新requirements.txt` |

**示例**:
```bash
git commit -m "feat: 实现RAG检索与生成模块"
git commit -m "fix: 修复ChromaDB批量添加限制问题"
git commit -m "docs: 编写Git使用手册"
```

### 3. 分支命名规范

| 分支类型 | 命名格式 | 示例 |
|----------|----------|------|
| 特性分支 | `feature/xxx` | `feature/rag-api` |
| 修复分支 | `bugfix/xxx` | `bugfix/pdf-parse` |
| 文档分支 | `docs/xxx` | `docs/readme` |
| 测试分支 | `test/xxx` | `test/embedding` |

### 4. 协作注意事项

1. **定期拉取**: 每天开始工作前执行 `git pull origin main`
2. **小提交**: 每个提交只包含一个逻辑单元的修改
3. **写清楚消息**: Commit消息要清晰描述做了什么
4. **代码审查**: 重要修改通过Pull Request进行审查
5. **冲突解决**: 遇到冲突时先拉取最新代码，手动解决冲突后再提交

## 四、SSH 配置说明

当前仓库使用SSH协议，需确保SSH密钥已正确配置：

### 检查SSH密钥
```bash
ls -la ~/.ssh/
```

### 生成SSH密钥（如果没有）
```bash
ssh-keygen -t ed25519 -C "15986655215@163.com"
```

### 添加密钥到ssh-agent
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### 将公钥添加到GitHub
复制 `~/.ssh/id_ed25519.pub` 的内容，粘贴到 GitHub Settings -> SSH and GPG keys 中

## 五、常见问题

### Q1: 推送失败，提示权限不足
**原因**: SSH密钥未正确配置或未添加到GitHub账户
**解决**: 检查SSH密钥配置，确保公钥已添加到GitHub

### Q2: 拉取时出现冲突
**解决**:
```bash
git pull origin main
# 手动编辑冲突文件，保留需要的代码
git add .
git commit -m "merge: 解决冲突"
git push origin main
```

### Q3: 误提交了敏感信息
**解决**: 使用 `git reset HEAD~1` 撤销最后一次提交（未推送时）

---

*文档版本: v1.0*
*最后更新: 2026-05-18*