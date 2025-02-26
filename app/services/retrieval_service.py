from typing import List, Dict, Any
import jieba
from rank_bm25 import BM25Okapi
from app.services.milvus_service import MilvusService
from app.services.embedding_service import EmbeddingService
from app.config.settings import settings

class RetrievalService:
    def __init__(self):
        self.milvus_service = MilvusService()
        self.embedding_service = EmbeddingService()
        self.vector_weight = settings.VECTOR_SEARCH_WEIGHT
        self.bm25_weight = settings.BM25_WEIGHT

    def _tokenize(self, text: str) -> List[str]:
        """使用jieba分词"""
        return list(jieba.cut(text))

    async def _bm25_search(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """使用BM25算法进行检索"""
        # 对查询和文档进行分词
        tokenized_query = self._tokenize(query)
        tokenized_documents = [self._tokenize(doc) for doc in documents]
        
        # 创建BM25模型
        bm25 = BM25Okapi(tokenized_documents)
        
        # 计算得分
        scores = bm25.get_scores(tokenized_query)
        
        # 将文档和得分组合，并按得分排序
        results = [
            {"content": documents[i], "score": float(scores[i])}
            for i in range(len(documents))
        ]
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]

    async def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """混合检索（向量检索 + BM25）"""
        # 1. 向量检索
        query_embedding = await self.embedding_service.get_embedding(query)
        vector_results = await self.milvus_service.search_similar(query_embedding, top_k=top_k)
        
        # 2. BM25检索
        documents = [result["content"] for result in vector_results]
        bm25_results = await self._bm25_search(query, documents, top_k=top_k)
        
        # 3. 合并结果
        merged_results = {}
        for i, vec_result in enumerate(vector_results):
            doc_id = vec_result["doc_id"]
            merged_results[doc_id] = {
                "content": vec_result["content"],
                "vector_score": vec_result["score"],
                "bm25_score": 0.0,
                "final_score": 0.0
            }
        
        for i, bm25_result in enumerate(bm25_results):
            content = bm25_result["content"]
            for doc_id, result in merged_results.items():
                if result["content"] == content:
                    result["bm25_score"] = bm25_result["score"]
                    break
        
        # 4. 计算最终得分
        for result in merged_results.values():
            result["final_score"] = (
                self.vector_weight * result["vector_score"] +
                self.bm25_weight * result["bm25_score"]
            )
        
        # 5. 按最终得分排序
        final_results = list(merged_results.values())
        final_results.sort(key=lambda x: x["final_score"], reverse=True)
        
        # 6. 重排序
        if len(final_results) > 0:
            reranked_results = await self.embedding_service.rerank_chunks(
                query,
                [result["content"] for result in final_results[:top_k]]
            )
            
            # 更新最终结果
            final_results = [
                {
                    "content": content,
                    "score": score
                }
                for content, score in reranked_results
            ]
        
        return final_results[:settings.FINAL_CHUNKS_COUNT]
