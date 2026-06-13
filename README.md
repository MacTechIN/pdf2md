# pdf2md

Microsoft [markitdown](https://github.com/microsoft/markitdown) 의 핵심 기술을 이용해
PDF 파일을 Markdown 텍스트로 변환하는 경량 래퍼 패키지입니다.

Markdown은 거의 일반 텍스트에 가까우면서도 문서의 구조(제목, 목록, 표, 링크 등)를
보존할 수 있어 LLM의 토큰 사용량을 크게 줄이는 데 적합합니다.

## 설치

이 컴퓨터의 Python 환경에서 다른 프로젝트에서도 불러 쓸 수 있도록 설치합니다.

```bash
# 현재 폴터에서 개발( editable ) 설치
python -m pip install -e .

# 또는 완전 설치
python -m pip install .
```

## 사용법

### Python API

```python
from pdf2md import pdf_to_markdown, convert_pdf, batch_convert

# Markdown 문자열로 받기
md_text = pdf_to_markdown("document.pdf")
print(md_text)

# 파일로 저장 (document.md 생성)
convert_pdf("document.pdf")

# 지정 경로로 저장
convert_pdf("document.pdf", "output/document.md")

# 여러 파일 일괄 변환
batch_convert(["a.pdf", "b.pdf"], output_dir="markdowns/")
```

### CLI

```bash
# 같은 이름의 .md 파일로 저장
pdf2md document.pdf

# 출력 파일 지정
pdf2md document.pdf output.md

# 플러그인 활성화
pdf2md document.pdf --plugins
```

## 의존성

- Python >= 3.10
- `markitdown[pdf]`
