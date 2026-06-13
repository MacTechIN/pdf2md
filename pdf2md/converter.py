"""PDF → Markdown 변환 핵심 모듈."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from markitdown import MarkItDown


class Pdf2MdConverter:
    """Microsoft MarkItDown 기반 PDF → Markdown 변환기."""

    def __init__(self, enable_plugins: bool = False):
        self._md = MarkItDown(enable_plugins=enable_plugins)

    def convert(self, pdf_path: str | Path) -> str:
        """단일 PDF 파일을 Markdown 문자열로 변환합니다."""
        path = Path(pdf_path)
        if not path.is_file():
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {path}")
        result = self._md.convert(str(path))
        return result.text_content

    def convert_and_save(
        self,
        pdf_path: str | Path,
        output_path: str | Path | None = None,
        encoding: str = "utf-8",
    ) -> Path:
        """PDF를 변환하고 파일로 저장합니다. output_path가 없으면 동일한 이름의 .md로 저장합니다."""
        path = Path(pdf_path)
        md_text = self.convert(path)

        if output_path is None:
            output_path = path.with_suffix(".md")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_text, encoding=encoding)
        return output_path


def pdf_to_markdown(pdf_path: str | Path, enable_plugins: bool = False) -> str:
    """단일 PDF 파일을 Markdown 문자열로 변환합니다."""
    return Pdf2MdConverter(enable_plugins=enable_plugins).convert(pdf_path)


def convert_pdf(
    pdf_path: str | Path,
    output_path: str | Path | None = None,
    enable_plugins: bool = False,
    encoding: str = "utf-8",
) -> Path:
    """단일 PDF 파일을 Markdown 파일로 변환합니다."""
    return Pdf2MdConverter(enable_plugins=enable_plugins).convert_and_save(
        pdf_path, output_path, encoding=encoding
    )


def batch_convert(
    pdf_paths: Iterable[str | Path],
    output_dir: str | Path | None = None,
    enable_plugins: bool = False,
    encoding: str = "utf-8",
) -> list[Path]:
    """여러 PDF 파일을 일괄 변환합니다."""
    converter = Pdf2MdConverter(enable_plugins=enable_plugins)
    results: list[Path] = []

    for pdf_path in pdf_paths:
        pdf_path = Path(pdf_path)
        if output_dir is not None:
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            output_path = out_dir / pdf_path.with_suffix(".md").name
        else:
            output_path = None

        results.append(
            converter.convert_and_save(pdf_path, output_path, encoding=encoding)
        )

    return results
