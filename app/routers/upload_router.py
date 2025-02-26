from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_processing import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.milvus_service import MilvusService
from app.utils.file_validation import validate_file
from app.models.schemas import UploadResponse
import uuid

router = APIRouter()
document_processor = DocumentProcessor()
embedding_service = EmbeddingService()
milvus_service = MilvusService()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """
    上传文档接口
    """
    try:
        # 1. 验证文件
        safe_filename = validate_file(file)
        
        # 2. 保存文件
        file_content = await file.read()
        file_path = await document_processor.save_uploaded_file(file_content, safe_filename)
        
        # 3. 处理文档
        doc_id, content, chunks = await document_processor.process_document(file_path, file.filename)
        
        # 4. 生成嵌入向量
        embeddings = await embedding_service.get_embeddings_batch(chunks)
        
        # 5. 准备存储数据
        chunk_data = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())
            chunk_data.append({
                "id": str(uuid.uuid4()),  # 主键ID
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "content": chunk,
                "embedding": embedding
            })
        
        # 6. 存储到Milvus
        await milvus_service.insert_chunks(chunk_data)
        
        return UploadResponse(
            message="文档上传并处理成功",
            document_id=doc_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
