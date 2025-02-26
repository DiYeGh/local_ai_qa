import aiohttp
from typing import List, Dict, Any
from app.config.settings import settings
from app.services.retrieval_service import RetrievalService

class AIService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.retrieval_service = RetrievalService()

    def _build_prompt(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """构建提示词"""
        context = "\n\n".join([chunk["content"] for chunk in context_chunks])
        
        prompt = f"""你是一个专业的AI助手。请基于以下提供的上下文信息，回答用户的问题。
如果上下文信息不足以回答问题，请明确告知。
请保持专业、准确和简洁的回答风格。

上下文信息：
{context}

用户问题：
{query}

回答："""
        
        return prompt

    async def generate_answer(self, query: str) -> Dict[str, Any]:
        """生成答案"""
        # 1. 检索相关文档块
        relevant_chunks = await self.retrieval_service.hybrid_search(query)
        
        if not relevant_chunks:
            return {
                "answer": "抱歉，我没有找到相关的信息来回答您的问题。",
                "source_chunks": []
            }
        
        # 2. 构建提示词
        prompt = self._build_prompt(query, relevant_chunks)
        
        # 3. 调用AI模型生成回答
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status != 200:
                        raise Exception(f"生成答案失败：{await response.text()}")
                    
                    result = await response.json()
                    answer = result["response"].strip()
                    
                    return {
                        "answer": answer,
                        "source_chunks": [chunk["content"] for chunk in relevant_chunks]
                    }
                    
        except Exception as e:
            return {
                "answer": f"生成答案时发生错误：{str(e)}",
                "source_chunks": []
            }
