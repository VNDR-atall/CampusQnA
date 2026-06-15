from typing import List, Dict, Generator
from openai import OpenAI, APIConnectionError, APIError, Timeout
from .vector_store import VectorStore
from .config import Config
import time

class RAGSystem:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=f"{Config.DEEPSEEK_BASE_URL}/v1",
            timeout=30
        )
    
    def _build_prompt(self, query: str, context_chunks: List[Dict]) -> str:
        context_str = ""
        for i, chunk in enumerate(context_chunks):
            source = chunk["metadata"].get("title", "未知来源")
            department = chunk["metadata"].get("department", "")
            context_str += f"[参考资料{i+1}]\n来源：{department}/{source}\n内容：{chunk['document']}\n\n"
        
        prompt = f"""你是一个校园信息助手，请根据以下参考资料回答用户问题。

参考资料：
{context_str}

用户问题：{query}

请按照以下规则回答：
1. 只能使用参考资料中的信息进行回答，不要编造内容；
2. 如果参考资料中没有足够的信息回答问题，请明确告知用户"暂无资料，无法回答"；
3. 在回答末尾列出引用的来源，格式为：【来源：部门/文件名】；
4. 回答要简洁明了，用自然语言表达。
"""
        return prompt
    
    def retrieve(self, query: str) -> List[Dict]:
        start_time = time.time()
        result = self.vector_store.query(query, top_k=Config.TOP_K)
        elapsed = time.time() - start_time
        print(f"向量检索耗时: {elapsed:.2f}秒")
        return result
    
    def generate(self, query: str, context_chunks: List[Dict]) -> str:
        if not context_chunks:
            return "暂无资料，无法回答", []
        
        prompt = self._build_prompt(query, context_chunks)
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的校园信息助手，擅长根据提供的资料回答问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
                timeout=60
            )
            
            elapsed = time.time() - start_time
            print(f"API调用耗时: {elapsed:.2f}秒")
            
            answer = response.choices[0].message.content.strip()
            
            sources = []
            for chunk in context_chunks:
                source_info = {
                    "title": chunk["metadata"].get("title", ""),
                    "department": chunk["metadata"].get("department", ""),
                    "source": chunk["metadata"].get("source", "")
                }
                sources.append(source_info)
            
            return answer, sources
        
        except Timeout:
            elapsed = time.time() - start_time
            print(f"API调用超时: {elapsed:.2f}秒")
            return "请求超时，请稍后再试", []
        except APIConnectionError as e:
            print(f"网络连接错误: {str(e)}")
            return "网络连接失败，请检查网络后重试", []
        except APIError as e:
            print(f"API错误: {str(e)}")
            return f"服务暂时不可用: {str(e)}", []
        except Exception as e:
            print(f"回答生成失败：{str(e)}")
            return "服务异常，请稍后再试", []
    
    def generate_stream(self, query: str, context_chunks: List[Dict]) -> Generator[str, None, None]:
        if not context_chunks:
            yield "暂无资料，无法回答"
            return
        
        prompt = self._build_prompt(query, context_chunks)
        
        try:
            stream = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的校园信息助手，擅长根据提供的资料回答问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
                stream=True,
                timeout=60
            )
            
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        
        except Exception as e:
            print(f"流式响应失败：{str(e)}")
            yield f"服务异常：{str(e)}"
    
    def query(self, query: str) -> Dict:
        print(f"收到查询: {query}")
        start_time = time.time()
        
        context_chunks = self.retrieve(query)
        
        if not context_chunks or all(chunk.get("distance", 1.0) > 0.8 for chunk in context_chunks):
            elapsed = time.time() - start_time
            print(f"查询完成（无结果）: {elapsed:.2f}秒")
            return {
                "answer": "暂无资料，无法回答",
                "sources": [],
                "context": []
            }
        
        answer, sources = self.generate(query, context_chunks)
        
        elapsed = time.time() - start_time
        print(f"查询完成: {elapsed:.2f}秒")
        
        return {
            "answer": answer,
            "sources": sources,
            "context": context_chunks
        }