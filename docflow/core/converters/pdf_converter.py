"""PDF to Markdown converter."""

import re
from pathlib import Path
from typing import Optional

from docflow.core.converters.base import BaseConverter
from docflow.core.models import (
    ConversionOptions,
    ConversionResult,
    DocumentMetadata,
    ImageInfo,
)

try:
    import fitz  # PyMuPDF
    import pdfplumber
    HAS_PDF_LIBS = True
except ImportError:
    HAS_PDF_LIBS = False


class PDFConverter(BaseConverter):
    """Convert PDF documents to Markdown."""

    def convert(self, source_path: Path, output_path: Path) -> ConversionResult:
        """Convert a PDF document to Markdown."""
        if not HAS_PDF_LIBS:
            return self._create_error_result(
                source_path,
                output_path,
                ["PDF libraries not installed. Run: pip install pdfplumber PyMuPDF"],
            )

        try:
            return self._convert_with_pdfplumber(source_path, output_path)
        except Exception as e:
            return self._create_error_result(
                source_path, output_path, [f"PDF conversion error: {str(e)}"]
            )

    def _convert_with_pdfplumber(
        self, source_path: Path, output_path: Path
    ) -> ConversionResult:
        """Convert PDF using pdfplumber for text and tables."""
        markdown_parts = []
        images = []
        warnings = []

        with pdfplumber.open(source_path) as pdf:
            metadata = self._extract_metadata(source_path, pdf)
            total_pages = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, 1):
                page_header = f"\n\n---\n\n## Page {page_num}\n\n"
                markdown_parts.append(page_header)

                # Extract text
                text = page.extract_text() or ""
                if text:
                    # Clean up and format text
                    text = self._clean_text(text)
                    markdown_parts.append(text)

                # Extract tables if enabled
                if self.options.pdf_extract_tables:
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables, 1):
                        if table:
                            md_table = self._format_table(table)
                            markdown_parts.append(f"\n\n### Table {table_idx}\n\n{md_table}")

                # Extract images if enabled
                if self.options.extract_images:
                    page_images = self._extract_page_images(
                        page, page_num, source_path, output_path
                    )
                    images.extend(page_images)

        markdown_content = "".join(markdown_parts).strip()

        return self._create_success_result(
            source_path,
            output_path,
            markdown_content,
            metadata=metadata,
            images=images,
            pages_processed=total_pages,
            warnings=warnings,
        )

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r"[ \t]+", " ", text)
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split("\n")]
        # Remove empty lines at start/end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        # Join lines, preserving paragraph breaks
        result = []
        current_para = []
        for line in lines:
            if line:
                current_para.append(line)
            else:
                if current_para:
                    result.append(" ".join(current_para))
                    current_para = []
        if current_para:
            result.append(" ".join(current_para))
        return "\n\n".join(result)

    def _format_table(self, table: list[list[str]]) -> str:
        """Convert a table to Markdown format."""
        if not table:
            return ""

        # Clean table cells
        cleaned = []
        for row in table:
            cleaned_row = [str(cell).strip() if cell else "" for cell in row]
            cleaned.append(cleaned_row)

        if not cleaned:
            return ""

        # Create Markdown table
        header = cleaned[0]
        separator = ["---"] * len(header)
        body = cleaned[1:] if len(cleaned) > 1 else []

        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(separator) + " |",
        ]
        for row in body:
            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)

    def _extract_page_images(
        self,
        page,
        page_num: int,
        source_path: Path,
        output_path: Path,
    ) -> list[ImageInfo]:
        """Extract images from a PDF page."""
        images = []
        image_idx = 0

        try:
            # Use PyMuPDF for image extraction
            doc = fitz.open(source_path)
            page_obj = doc[page_num - 1]

            for img_info in page_obj.get_images():
                image_idx += 1
                xref = img_info[0]
                base_image = doc.extract_image(xref)

                if base_image:
                    img_data = base_image["image"]
                    img_ext = base_image["ext"]

                    # Save image
                    image_dir = output_path.parent / (self.options.image_dir or "images")
                    image_dir.mkdir(parents=True, exist_ok=True)

                    image_name = f"{source_path.stem}_p{page_num}_i{image_idx}.{img_ext}"
                    image_path = image_dir / image_name

                    with open(image_path, "wb") as f:
                        f.write(img_data)

                    images.append(
                        ImageInfo(
                            index=image_idx,
                            original_format=img_ext,
                            size_bytes=len(img_data),
                            extracted_path=image_path,
                        )
                    )
        except Exception:
            pass  # Silently skip image extraction errors

        return images

    def _extract_metadata(
        self, source_path: Path, pdf
    ) -> DocumentMetadata:
        """Extract metadata from PDF."""
        meta = pdf.metadata or {}

        return DocumentMetadata(
            title=meta.get("Title"),
            author=meta.get("Author"),
            subject=meta.get("Subject"),
            keywords=meta.get("Keywords", "").split(", ") if meta.get("Keywords") else [],
            creator=meta.get("Creator"),
            producer=meta.get("Producer"),
            page_count=len(pdf.pages),
            file_size=source_path.stat().st_size if source_path.exists() else None,
        )
