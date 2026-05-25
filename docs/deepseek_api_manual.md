# DeepSeek API 使用手册

## 一、什么是 DeepSeek API

DeepSeek API 是深度求索（DeepSeek）提供的大语言模型 API 服务，允许开发者通过 HTTP 接口调用其大语言模型进行文本生成、问答等任务。

**官方网站**: https://www.deepseek.com/
**API 文档**: https://platform.deepseek.com/docs/introduction

## 二、注册与获取 API Key

### 步骤 1：注册账号

1. 访问 DeepSeek 官方平台：https://platform.deepseek.com/
2. 点击右上角「登录/注册」
3. 使用邮箱或手机号注册账号
4. 完成邮箱验证

### 步骤 2：获取 API Key

1. 登录后，进入「控制台」
2. 点击左侧菜单「API Keys」
3. 点击「Create new key」创建新的 API Key
4. 复制生成的 API Key（**只显示一次，请妥善保存**）

### 注意事项

- **保密安全**: API Key 是您的身份凭证，请勿泄露给他人
- **额度管理**: 新用户有免费额度（约 500 万 tokens），注意监控使用量
- **多 Key 管理**: 可以创建多个 API Key 用于不同场景

## 三、API 配置

### 1. 配置到项目

在项目根目录的 `.env` 文件中配置：

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 2. 配置说明

| 配置项 | 值 | 说明 |
|--------|-----|------|
| DEEPSEEK_API_KEY | 您的 API Key | 必需配置 |
| DEEPSEEK_BASE_URL | https://api.deepseek.com | API 服务地址 |

## 四、API 调用流程

### 1. 基本调用方式

DeepSeek API 兼容 OpenAI API 格式，可以使用 `openai` Python 库调用：

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    base_url="https://api.deepseek.com/v1"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个专业的校园信息助手"},
        {"role": "user", "content": "图书馆开放时间是什么时候？"}
    ],
    temperature=0.1,
    max_tokens=1024
)

print(response.choices[0].message.content)
```

### 2. 在本项目中的调用

项目已封装好 RAG 系统，只需配置 API Key 即可使用：

```bash
# 配置 .env 文件后，启动命令行测试
python scripts/chat.py
```

### 3. API 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model | string | deepseek-chat | 模型名称 |
| messages | list | - | 消息列表 |
| temperature | float | 0.7 | 生成随机性，0-2，越小越确定 |
| max_tokens | int | 1024 | 最大生成 token 数 |
| stream | bool | false | 是否流式输出 |

### 4. 消息格式

```python
messages = [
    {"role": "system", "content": "系统提示词，定义助手角色"},
    {"role": "user", "content": "用户的问题"},
    {"role": "assistant", "content": "助手的回答（多轮对话时使用）"}
]
```

## 五、本项目中的 RAG 调用流程

### 完整流程

```
用户提问 → 向量化 → 向量检索 → 构建 Prompt → 调用 DeepSeek → 返回回答

1. 用户提问："计算机学院培养方案是什么？"
2. 向量化：将问题转为 512 维向量
3. 向量检索：在 ChromaDB 中查找最相似的 3 个文档片段
4. 构建 Prompt：将检索结果作为参考资料放入 Prompt
5. 调用 DeepSeek：发送请求，获取回答
6. 返回回答：包含答案和来源引用
```

### 代码实现

```python
# src/rag.py 中的关键代码

class RAGSystem:
    def __init__(self, vector_store):
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=f"{Config.DEEPSEEK_BASE_URL}/v1"
        )
    
    def generate(self, query, context_chunks):
        prompt = self._build_prompt(query, context_chunks)
        
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是专业的校园信息助手"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1024
        )
        
        return response.choices[0].message.content
```

## 六、测试 API

### 方法 1：使用命令行工具

```bash
# 确保已配置 .env
python scripts/chat.py

# 输入问题测试
请输入你的问题：计算机学院有哪些专业？
```

### 方法 2：使用 curl 测试

```bash
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -d '{
    "model": "deepseek-chat",
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

## 七、常见问题

### Q1: API Key 如何获取？
**答**: 登录 https://platform.deepseek.com/，进入控制台 -> API Keys -> Create new key

### Q2: 免费额度有多少？
**答**: 新用户注册后有 500 万 tokens 的免费额度

### Q3: API 调用失败怎么办？

**常见错误及解决方法：**

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `Invalid API Key` | API Key 错误或未配置 | 检查 `.env` 文件中的 API Key |
| `Insufficient quota` | 额度用尽 | 等待额度刷新或购买额度 |
| `Rate limit exceeded` | 请求过于频繁 | 降低请求频率 |
| `Connection timeout` | 网络问题 | 检查网络连接 |

### Q4: 如何查看使用额度？
**答**: 登录 DeepSeek 平台控制台，在「Usage」页面查看

### Q5: 是否支持流式输出？
**答**: 支持，设置 `stream=True` 即可

## 八、安全最佳实践

1. **不要硬编码 API Key**: 始终使用环境变量配置
2. **限制 API Key 权限**: 只授予必要的权限
3. **定期轮换 Key**: 定期创建新的 API Key，禁用旧的
4. **监控使用量**: 定期检查 API 使用情况，防止异常
5. **使用 HTTPS**: 所有 API 调用都使用 HTTPS

## 九、参考链接

- **DeepSeek 官网**: https://www.deepseek.com/
- **API 文档**: https://platform.deepseek.com/docs/introduction
- **模型列表**: https://platform.deepseek.com/docs/models
- **定价说明**: https://platform.deepseek.com/docs/pricing

---

*文档版本: v1.0*
*最后更新: 2026-05-18*