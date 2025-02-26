from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    content: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: str
    created_at: datetime
    file_path: str
    
    class Config:
        from_attributes = True

class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    content: str
    embedding: Optional[List[float]] = None
    
    class Config:
        from_attributes = True

class QuestionRequest(BaseModel):
    question: str = Field(..., description="用户的问题")
    
class AnswerResponse(BaseModel):
    answer: str = Field(..., description="AI生成的答案")
    source_chunks: List[str] = Field(..., description="用于生成答案的相关文档片段")
    
class UploadResponse(BaseModel):
    message: str
    document_id: str
    
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
