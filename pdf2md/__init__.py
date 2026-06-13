"""
pdf2md: PDF를 Markdown으로 변환하여 토큰을 줄이는 경량 래퍼 패키지.

Microsoft MarkItDown 의 핵심 기술(`markitdown.MarkItDown`)을 이용해
PDF 파일을 구조를 보존한 Markdown 텍스트로 변환합니다.
"""

from .converter import pdf_to_markdown, convert_pdf, batch_convert

__version__ = "0.1.0"
__all__ = ["pdf_to_markdown", "convert_pdf", "batch_convert"]
