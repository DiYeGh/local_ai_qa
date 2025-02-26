from typing import List, Dict, Any
from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility
)
from app.config.settings import settings

class MilvusService:
    def __init__(self):
        self.host = settings.MILVUS_HOST
        self.port = settings.MILVUS_PORT
        self.collection_name = settings.COLLECTION_NAME
        self.dim = settings.VECTOR_DIM
        self._ensure_connection()
        self._ensure_collection()

    def _ensure_connection(self):
        """确保与Milvus的连接"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
        except Exception as e:
            raise Exception(f"连接Milvus失败：{str(e)}")

    def _ensure_collection(self):
        """确保集合存在，如果不存在则创建"""
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=36, is_primary=True),
                FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=36),
                FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=36),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
            ]
            schema = CollectionSchema(fields=fields, description="文档块存储")
            collection = Collection(name=self.collection_name, schema=schema)
            
            # 创建IVF_FLAT索引
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            collection.create_index(field_name="embedding", index_params=index_params)

    async def insert_chunks(self, chunks: List[Dict[str, Any]]):
        """插入文档块"""
        collection = Collection(self.collection_name)
        
        try:
            collection.insert(chunks)
            collection.flush()
        except Exception as e:
            raise Exception(f"插入文档块失败：{str(e)}")

    async def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似文档块"""
        collection = Collection(self.collection_name)
        collection.load()
        
        try:
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["doc_id", "chunk_id", "content"]
            )
            
            hits = []
            for hit in results[0]:
                hits.append({
                    "doc_id": hit.entity.get("doc_id"),
                    "chunk_id": hit.entity.get("chunk_id"),
                    "content": hit.entity.get("content"),
                    "score": hit.score
                })
            
            return hits
            
        except Exception as e:
            raise Exception(f"搜索相似文档块失败：{str(e)}")
        finally:
            collection.release()

    async def delete_by_doc_id(self, doc_id: str):
        """删除指定文档的所有块"""
        collection = Collection(self.collection_name)
        try:
            expr = f'doc_id == "{doc_id}"'
            collection.delete(expr)
        except Exception as e:
            raise Exception(f"删除文档块失败：{str(e)}")

    def close(self):
        """关闭连接"""
        try:
            connections.disconnect("default")
        except Exception:
            pass
