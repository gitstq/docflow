"""Image to Markdown converter with OCR support."""

from pathlib import Path

from docflow.core.converters.base import BaseConverter
from docflow.core.models import DocumentMetadata, ImageInfo

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


class ImageConverter(BaseConverter):
    """Convert images to Markdown with optional OCR."""

    def convert(self, source_path: Path, output_path: Path):
        """Convert an image to Markdown."""
        if not HAS_PIL:
            return self._create_error_result(
                source_path,
                output_path,
                ["Pillow not installed. Run: pip install Pillow"],
            )

        try:
            image = Image.open(source_path)
            markdown_parts = []
            images = []

            # Add image reference
            image_dir = self.options.image_dir or "images"
            image_name = source_path.name
            markdown_parts.append(f"![{source_path.stem}]({image_dir}/{image_name})\n")

            # OCR if enabled
            ocr_text = None
            if self.options.enable_ocr and HAS_TESSERACT:
                try:
                    ocr_text = pytesseract.image_to_string(
                        image, lang=self.options.ocr_language
                    ).strip()
                    if ocr_text:
                        markdown_parts.append(f"\n### OCR Text\n\n{ocr_text}\n")
                except Exception as e:
                    markdown_parts.append(f"\n*OCR failed: {str(e)}*\n")

            # Get image info
            images.append(
                ImageInfo(
                    index=1,
                    original_format=image.format.lower() if image.format else "unknown",
                    width=image.width,
                    height=image.height,
                    size_bytes=source_path.stat().st_size if source_path.exists() else None,
                    ocr_text=ocr_text,
                )
            )

            metadata = DocumentMetadata(
                title=source_path.stem,
                file_size=source_path.stat().st_size if source_path.exists() else None,
            )

            return self._create_success_result(
                source_path,
                output_path,
                "".join(markdown_parts).strip(),
                metadata=metadata,
                images=images,
            )

        except Exception as e:
            return self._create_error_result(
                source_path, output_path, [f"Image conversion error: {str(e)}"]
            )
