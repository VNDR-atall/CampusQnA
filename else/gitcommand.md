在已经配置好 SSH 连接的 Git 仓库里，日常高频操作其实就集中在**查看状态、拉取更新、上传提交**这三类。下面按场景列出最常用的命令，假设你的远程地址类似 `git@github.com:user/repo.git`。

***

### 🔍 一、查看（了解仓库当前状态）

| 场景             | 命令                                | 说明                                          |
| :------------- | :-------------------------------- | :------------------------------------------ |
| 查看远程仓库配置       | `git remote -v`                   | 确认是否使用了 SSH 地址（以 `git@` 开头）                 |
| 测试 SSH 连接      | `ssh -T git@github.com`（或其他平台）    | 验证密钥是否正常，输出欢迎信息即成功                          |
| 查看所有分支         | `git branch -a`                   | 带 `remotes/origin` 的是远程分支                   |
| 查看本地分支与远程的跟踪关系 | `git branch -vv`                  | 能看到落后/超前几个提交                                |
| 查看工作区状态        | `git status`                      | 最常用，告诉你改了什么、哪些可提交                           |
| 查看提交历史         | `git log --oneline --graph --all` | 图形化查看所有分支的提交线                               |
| 查看某次提交的详情      | `git show <commit-id>`            | 查看具体修改内容                                    |
| 对比差异           | `git diff`                        | 工作区 vs 暂存区；`git diff --staged` 看暂存区 vs 最新提交 |

***

### 📥 二、拉取（从远程获取更新）

| 操作           | 命令                                            | 说明                                         |
| :----------- | :-------------------------------------------- | :----------------------------------------- |
| 仅下载远程更新（不合并） | `git fetch origin`                            | 安全操作，更新本地的远程追踪分支（如 `origin/main`）          |
| 下载并合并到当前分支   | `git pull`                                    | `git fetch` + `git merge` 的简写，**可能产生合并提交** |
| 下载并变基（推荐）    | `git pull --rebase`                           | 把你的本地新提交“嫁接”到远程最新提交之后，历史更线性                |
| 拉取指定分支       | `git pull origin main`                        | 远程 `main` 分支拉取到当前分支（或指定本地分支）               |
| 查看远程更新的内容    | `git fetch origin` 然后 `git log ..origin/main` | 合并前先看看远程多了哪些提交                             |

> 日常为了避免乱七八糟的合并提交，很多团队会设置 `git config --global pull.rebase true`，让 `git pull` 默认变基。

***

### 📤 三、上传（将本地提交推送到远程）

| 操作          | 命令                                           | 说明                           |
| :---------- | :------------------------------------------- | :--------------------------- |
| 推送当前分支到远程   | `git push`                                   | 前提是已经设置了上游分支（`-u` 设置过）       |
| 首次推送并建立跟踪   | `git push -u origin feature-branch`          | 之后就可以直接用 `git push`          |
| 推送到指定远程分支   | `git push origin local-branch:remote-branch` | 灵活指定不同名称                     |
| 强制推送（⚠️ 谨慎） | `git push --force-with-lease`                | 比 `--force` 安全，会检查远程是否被他人更新过 |
| 删除远程分支      | `git push origin --delete old-branch`        | 清理不需要的远程分支                   |
| 推送所有本地分支    | `git push --all origin`                      | 一次性把所有本地分支推上去（少用）            |
| 推送标签        | `git push --tags`                            | 把本地所有 tag 推送到远程              |

***

### 🔁 一个日常的典型流程

```bash
# 1. 看看仓库是不是最新，有没有别人的更新
git fetch origin

# 2. 查看当前分支状态
git status

# 3. 合并远程更新（比如主分支有更新）
git pull --rebase origin main

# 4. 开始修改代码... 之后
git add .
git commit -m "完成xxx功能"

# 5. 推送自己的分支
git push -u origin main    # 第一次推送
git push                         # 后续推送
```

***

### 🛠️ 小贴士

- 如果 `git push` 或 `git pull` 提示权限问题，先执行 `ssh -T git@your-host` 确认 SSH 密钥是否已添加并激活。
- 遇到冲突不要慌，`git status` 会列出冲突文件，手动解决后 `git add` 标记解决，再 `git rebase --continue`（如果用的 rebase）或 `git merge --continue`。

如果有特定平台（如 GitHub、GitLab、Gitee）的特殊操作需求，或者想了解分支管理、标签操作，可以继续问我。
