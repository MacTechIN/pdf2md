"""CLI: python -m pdf2md <pdf_path> [output_path]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import convert_pdf


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PDF를 Markdown으로 변환하여 토큰 사용량을 줄입니다."
    )
    parser.add_argument("pdf", help="입력 PDF 파일 경로")
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="출력 Markdown 파일 경로 (미지정 시 입력 파일명.md)",
    )
    parser.add_argument(
        "--plugins",
        action="store_true",
        help="MarkItDown 플러그인 활성화",
    )

    args = parser.parse_args(argv)

    output = convert_pdf(
        pdf_path=args.pdf,
        output_path=args.output,
        enable_plugins=args.plugins,
    )
    print(output.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
