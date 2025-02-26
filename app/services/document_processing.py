import os
from typing import List, Tuple
import docx
from app.utils.text_splitter import TextSplitter
from app.config.settings import settings
import uuid


class DocumentProcessor:
    def __init__(self):
        self.text_splitter = TextSplitter()

    def process_txt(self, file_path: str) -> Tuple[str, List[str]]:
        """处理TXT文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, self.text_splitter.split_text(content)

    def process_docx(self, file_path: str) -> Tuple[str, List[str]]:
        """处理DOCX文件"""
        doc = docx.Document(file_path)
        content = "\n\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
        return content, self.text_splitter.split_text(content)

    async def process_document(self, file_path: str, original_filename: str) -> Tuple[str, str, List[str]]:
        """处理文档主函数"""
        # 生成文档ID
        doc_id = str(uuid.uuid4())

        # 根据文件扩展名选择处理方法
        file_ext = os.path.splitext(original_filename)[1].lower()

        try:
            if file_ext == '.txt':
                content, chunks = self.process_txt(file_path)
            elif file_ext == '.docx':
                content, chunks = self.process_docx(file_path)
            else:
                raise ValueError(f"不支持的文件类型：{file_ext}")

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
