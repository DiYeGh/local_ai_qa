import os
from typing import List, Tuple
import docx
from app.utils.text_splitter import TextSplitter
from app.config.settings import settings
import uuid
from app.utils.extract_text import extract_text_from_file


class DocumentProcessor:
    def __init__(self):
        self.text_splitter = TextSplitter()

    async def process_document(self, file_path: str, original_filename: str) -> Tuple[str, str, List[str]]:
        """处理文档主函数"""
        # 生成文档ID
        doc_id = str(uuid.uuid4())

        try:
            # 使用通用文本提取函数
            content = extract_text_from_file(file_path)
            if not content:
                raise ValueError(f"无法提取文件内容：{original_filename}")
            
            # 分割文本
            chunks = self.text_splitter.split_text(content)
            
            return doc_id, content, chunks

        except Exception as e:
            # 如果处理失败，删除上传的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            raise Exception(f"文档处理失败：{str(e)}")

    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """保存上传的文件"""
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        try:
            with open(file_path, 'wb') as f:
                f.write(file_content)
            return file_path
        except Exception as e:
            raise Exception(f"文件保存失败：{str(e)}")
