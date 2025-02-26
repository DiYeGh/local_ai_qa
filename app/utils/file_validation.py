from fastapi import HTTPException, UploadFile
from app.config.settings import settings
import os

def validate_file_size(file: UploadFile) -> None:
    """验证文件大小是否在限制范围内"""
    # 获取文件大小
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()  # 获取文件大小
    file.file.seek(0)  # 重置文件指针到开头
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制：{settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )

def validate_file_extension(filename: str) -> None:
    """验证文件扩展名是否允许"""
    ext = filename.split('.')[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型。允许的文件类型：{', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

def get_safe_filename(filename: str) -> str:
    """生成安全的文件名，避免文件名冲突"""
    base_name = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(settings.UPLOAD_DIR, new_filename)):
        new_filename = f"{base_name}_{counter}{extension}"
        counter += 1
        
    return new_filename

def validate_file(file: UploadFile) -> str:
    """完整的文件验证流程"""
    validate_file_extension(file.filename)
    validate_file_size(file)
    safe_filename = get_safe_filename(file.filename)
    return safe_filename
