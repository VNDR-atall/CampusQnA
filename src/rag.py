from typing import List, Dict
from openai import OpenAI
from .vector_store import VectorStore
from .config import Config

class RAGSystem:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=f"{Config.DEEPSEEK_BASE_URL}/v1"
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
        return self.vector_store.query(query, top_k=Config.TOP_K)
    
    def generate(self, query: str, context_chunks: List[Dict]) -> str:
        if not context_chunks:
            return "暂无资料，无法回答", []
        
        prompt = self._build_prompt(query, context_chunks)
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的校园信息助手，擅长根据提供的资料回答问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024
            )
            
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
        
        except Exception as e:
            return f"回答生成失败：{str(e)}", []
    
    def query(self, query: str) -> Dict:
        context_chunks = self.retrieve(query)
        
        if not context_chunks or all(chunk.get("distance", 1.0) > 0.8 for chunk in context_chunks):
            return {
                "answer": "暂无资料，无法回答",
                "sources": [],
                "context": []
            }
        
        answer, sources = self.generate(query, context_chunks)
        
        return {
            "answer": answer,
            "sources": sources,
            "context": context_chunks
        }