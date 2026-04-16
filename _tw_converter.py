"""Main converter engine for DocFlow."""

import time
from pathlib import Path
from typing import List, Optional, Union

from docflow.core.converters.base import BaseConverter
from docflow.core.converters.csv_converter import CSVConverter
from docflow.core.converters.excel_converter import ExcelConverter
from docflow.core.converters.html_converter import HTMLConverter
from docflow.core.converters.image_converter import ImageConverter
from docflow.core.converters.pdf_converter import PDFConverter
from docflow.core.converters.powerpoint_converter import PowerPointConverter
from docflow.core.converters.text_converter import TextConverter
from docflow.core.converters.word_converter import WordConverter
from docflow.core.models import (
    BatchConversionResult,
    ConversionOptions,
    ConversionResult,
    ConversionStatus,
    DocumentFormat,
)
from docflow.utils.file_utils import detect_format, ensure_dir, get_file_hash
from docflow.utils.logger import get_logger

logger = get_logger(__name__)


class DocFlowConverter:
    """
    Main converter class for converting documents to Markdown.

    Supports multiple input formats including PDF, Word, PowerPoint, Excel,
    HTML, images (with OCR), and plain text files.

    Example:
        >>> converter = DocFlowConverter()
        >>> result = converter.convert("document.pdf")
        >>> print(result.markdown_content)
    """

    # Mapping of document formats to converter classes
    CONVERTER_MAP = {
        DocumentFormat.PDF: PDFConverter,
        DocumentFormat.DOCX: WordConverter,
        DocumentFormat.PPTX: PowerPointConverter,
        DocumentFormat.XLSX: ExcelConverter,
        DocumentFormat.HTML: HTMLConverter,
        DocumentFormat.HTM: HTMLConverter,
        DocumentFormat.TXT: TextConverter,
        DocumentFormat.MD: TextConverter,
        DocumentFormat.MARKDOWN: TextConverter,
        DocumentFormat.CSV: CSVConverter,
        DocumentFormat.TSV: CSVConverter,
        DocumentFormat.JSON: TextConverter,
        DocumentFormat.XML: TextConverter,
        DocumentFormat.PNG: ImageConverter,
        DocumentFormat.JPG: ImageConverter,
        DocumentFormat.JPEG: ImageConverter,
        DocumentFormat.GIF: ImageConverter,
        DocumentFormat.BMP: ImageConverter,
        DocumentFormat.TIFF: ImageConverter,
        DocumentFormat.WEBP: ImageConverter,
    }

    def __init__(self, options: Optional[ConversionOptions] = None) -> None:
        """
        Initialize the DocFlow converter.

        Args:
            options: Conversion options. If not provided, defaults will be used.
        """
        self.options = options or ConversionOptions()
        self._converters: dict[DocumentFormat, BaseConverter] = {}

    def get_converter(self, format_type: DocumentFormat) -> BaseConverter:
        """
        Get or create a converter for the specified format.

        Args:
            format_type: The document format.

        Returns:
            A converter instance for the format.
        """
        if format_type not in self._converters:
            converter_class = self.CONVERTER_MAP.get(format_type)
            if converter_class is None:
                raise ValueError(f"Unsupported format: {format_type}")
            self._converters[format_type] = converter_class(self.options)
        return self._converters[format_type]

    def convert(
        self,
        source: Union[str, Path],
        output: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> ConversionResult:
        """
        Convert a single document to Markdown.

        Args:
            source: Path to the source document.
            output: Optional path for the output Markdown file.
            **kwargs: Additional options to override instance options.

        Returns:
            A ConversionResult containing the conversion output and metadata.
        """
        source_path = Path(source)
        start_time = time.time()

        # Validate source file
        if not source_path.exists():
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                status=ConversionStatus.FAILED,
                errors=[f"Source file not found: {source_path}"],
                processing_time_seconds=time.time() - start_time,
            )

        # Detect format
        try:
            format_type = detect_format(source_path)
        except ValueError as e:
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                status=ConversionStatus.FAILED,
                errors=[str(e)],
                processing_time_seconds=time.time() - start_time,
            )

        # Determine output path
        if output:
            output_path = Path(output)
        elif self.options.output_dir:
            output_path = self.options.output_dir / f"{source_path.stem}.md"
        else:
            output_path = source_path.with_suffix(".md")

        logger.info(f"Converting {source_path} ({format_type.value}) -> {output_path}")

        try:
            # Get appropriate converter
            converter = self.get_converter(format_type)

            # Perform conversion
            result = converter.convert(source_path, output_path)

            # Calculate processing time
            result.processing_time_seconds = time.time() - start_time

            # Save output if content was generated
            if result.markdown_content and result.status != ConversionStatus.FAILED:
                ensure_dir(output_path.parent)
                output_path.write_text(result.markdown_content, encoding="utf-8")
                result.output_path = output_path

                # Update status if output was created
                if output_path.exists():
                    result.status = ConversionStatus.SUCCESS
                else:
                    result.status = ConversionStatus.FAILED
                    result.errors.append("Failed to write output file")

            logger.info(
                f"Conversion complete: {result.status.value} "
                f"({result.processing_time_seconds:.2f}s)"
            )

            return result

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                status=ConversionStatus.FAILED,
                errors=[str(e)],
                processing_time_seconds=time.time() - start_time,
            )

    def convert_batch(
        self,
        sources: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> BatchConversionResult:
        """
        Convert multiple documents in batch.

        Args:
            sources: List of paths to source documents.
            output_dir: Optional output directory for all converted files.
            **kwargs: Additional options to override instance options.

        Returns:
            A BatchConversionResult containing all individual results and summary.
        """
        batch_result = BatchConversionResult()

        # Override output directory if provided
        original_output_dir = self.options.output_dir
        if output_dir:
            self.options.output_dir = Path(output_dir)
            ensure_dir(self.options.output_dir)

        try:
            for source in sources:
                result = self.convert(source, **kwargs)
                batch_result.add_result(result)

        finally:
            # Restore original output directory
            self.options.output_dir = original_output_dir

        logger.info(
            f"Batch conversion complete: {batch_result.successful} successful, "
            f"{batch_result.partial} partial, {batch_result.failed} failed, "
            f"{batch_result.skipped} skipped"
        )

        return batch_result

    def convert_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = True,
        pattern: str = "*",
        output_dir: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> BatchConversionResult:
        """
        Convert all supported documents in a directory.

        Args:
            directory: Path to the directory to process.
            recursive: Whether to process subdirectories.
            pattern: Glob pattern to filter files.
            output_dir: Optional output directory for converted files.
            **kwargs: Additional options.

        Returns:
            A BatchConversionResult containing all conversion results.
        """
        dir_path = Path(directory)

        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {dir_path}")

        # Collect all files
        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))

        # Filter to supported formats
        supported_files = []
        for file_path in files:
            if file_path.is_file():
                try:
                    detect_format(file_path)
                    supported_files.append(file_path)
                except ValueError:
                    # Skip unsupported formats silently
                    pass

        logger.info(f"Found {len(supported_files)} supported files in {dir_path}")

        return self.convert_batch(supported_files, output_dir, **kwargs)

    @classmethod
    def get_supported_formats(cls) -> List[DocumentFormat]:
        """
        Get a list of all supported document formats.

        Returns:
            List of supported DocumentFormat enums.
        """
        return list(cls.CONVERTER_MAP.keys())

    @classmethod
    def is_supported(cls, file_path: Union[str, Path]) -> bool:
        """
        Check if a file format is supported.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the format is supported, False otherwise.
        """
        try:
            detect_format(file_path)
            return True
        except ValueError:
            return False
