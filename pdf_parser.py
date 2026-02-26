"""PDF解析模块 - 提取PDF文本内容"""
import io
from PyPDF2 import PdfReader
import re


def extract_text_from_pdf(pdf_file) -> str:
    """从PDF文件中提取文本内容"""
    try:
        if isinstance(pdf_file, bytes):
            pdf_file = io.BytesIO(pdf_file)
        
        reader = PdfReader(pdf_file)
        text_content = []
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
        
        return "\n".join(text_content)
    except Exception as e:
        raise Exception(f"PDF解析失败: {str(e)}")


def clean_text(text: str) -> str:
    """清洗和结构化处理文本"""
    # 去除多余空白字符
    text = re.sub(r'\s+', ' ', text)
    # 去除特殊字符但保留中文标点
    text = re.sub(r'[^\w\s\u4e00-\u9fff，。、；：""''（）【】@.\-+]', '', text)
    # 分段处理
    text = re.sub(r'\s*\n\s*', '\n', text)
    return text.strip()
