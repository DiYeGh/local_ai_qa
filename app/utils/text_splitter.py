from typing import List
import re
from app.config.settings import settings

class TextSplitter:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_by_paragraph(self, text: str) -> List[str]:
        """按段落分割文本"""
        # 使用多个换行符作为段落分隔符
        paragraphs = re.split(r'\n\s*\n', text.strip())
        # 过滤掉空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs

    def merge_short_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """合并过短的段落"""
        result = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += para
            else:
                if current_chunk:
                    result.append(current_chunk)
                current_chunk = para
        
        if current_chunk:
            result.append(current_chunk)
        
        return result

    def split_long_paragraph(self, paragraph: str) -> List[str]:
        """将过长的段落按句子分割"""
        # 中文句子分隔符
        sentence_endings = r'[。！？!?]+'
        sentences = re.split(f'({sentence_endings})', paragraph)
        chunks = []
        current_chunk = ""
        
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            # 如果是句子结束符，将其附加到当前句子
            if i + 1 < len(sentences) and re.match(sentence_endings, sentences[i + 1]):
                sentence += sentences[i + 1]
                i += 1
            
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
            i += 1
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    def split_text(self, text: str) -> List[str]:
        """主分割函数"""
        # 1. 首先按段落分割
        paragraphs = self.split_by_paragraph(text)
        chunks = []
        
        # 2. 处理每个段落
        for para in paragraphs:
            # 如果段落长度超过chunk_size，需要进一步分割
            if len(para) > self.chunk_size:
                chunks.extend(self.split_long_paragraph(para))
            else:
                chunks.append(para)
        
        # 3. 合并过短的块
        chunks = self.merge_short_paragraphs(chunks)
        
        # 4. 确保所有块都不超过最大长度
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.chunk_size:
                final_chunks.extend(self.split_long_paragraph(chunk))
            else:
                final_chunks.append(chunk)
        
        return final_chunks
