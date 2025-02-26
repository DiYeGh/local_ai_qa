import aiohttp
import json
from typing import List, Tuple
import numpy as np
from app.config.settings import settings

class EmbeddingService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.EMBEDDING_MODEL

    async def get_embedding(self, text: str) -> List[float]:
        """获取单个文本的嵌入向量"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                }
            ) as response:
                if response.status != 200:
                    raise Exception(f"获取嵌入向量失败：{await response.text()}")
                
                result = await response.json()
                return result["embedding"]

    async def get_embeddings_batch(self, texts: List[str], batch_size: int = 5) -> List[List[float]]:
        """批量获取文本的嵌入向量"""
        embeddings = []
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await asyncio.gather(
                *[self.get_embedding(text) for text in batch]
            )
            embeddings.extend(batch_embeddings)
        
        return embeddings

    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """计算两个向量之间的余弦相似度"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        return dot_product / (norm1 * norm2)

    async def rerank_chunks(self, query: str, chunks: List[str]) -> List[Tuple[str, float]]:
        """使用重排序模型对文档块进行重新排序"""
        async with aiohttp.ClientSession() as session:
            results = []
            for chunk in chunks:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": settings.RERANK_MODEL,
                        "prompt": f"Query: {query}\nDocument: {chunk}\nScore:",
                        "stream": False
                    }
                ) as response:
                    if response.status != 200:
                        raise Exception(f"重排序失败：{await response.text()}")
                    
                    result = await response.json()
                    # 解析分数（假设模型返回0-1之间的分数）
                    try:
                        score = float(result["response"].strip())
                        results.append((chunk, score))
                    except ValueError:
                        results.append((chunk, 0.0))
            
            # 按分数降序排序
            results.sort(key=lambda x: x[1], reverse=True)
            return results
