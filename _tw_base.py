"""Base converter class for all document converters."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from docflow.core.models import (
    ConversionOptions,
    ConversionResult,
    ConversionStatus,
    DocumentMetadata,
    ImageInfo,
)


class BaseConverter(ABC):
    """
    Abstract base class for all document converters.

    Each converter must implement the convert method to handle its specific format.
    """

    def __init__(self, options: Optional[ConversionOptions] = None) -> None:
        """
        Initialize the converter.

        Args:
            options: Conversion options.
        """
        self.options = options or ConversionOptions()

    @abstractmethod
    def convert(self, source_path: Path, output_path: Path) -> ConversionResult:
        """
        Convert a document to Markdown.

        Args:
            source_path: Path to the source document.
            output_path: Path where the output Markdown will be saved.

        Returns:
            A ConversionResult with the conversion output.
        """
        pass

    def extract_metadata(self, source_path: Path) -> Optional[DocumentMetadata]:
        """
        Extract metadata from the source document.

        Override this method in subclasses to extract format-specific metadata.

        Args:
            source_path: Path to the source document.

        Returns:
            A DocumentMetadata object, or None if metadata extraction is not supported.
        """
        return None

    def extract_images(
        self, source_path: Path, output_dir: Path
    ) -> list[ImageInfo]:
        """
        Extract embedded images from the source document.

        Override this method in subclasses to extract images.

        Args:
            source_path: Path to the source document.
            output_dir: Directory to save extracted images.

        Returns:
            List of ImageInfo objects for extracted images.
        """
        return []

    def _create_success_result(
        self,
        source_path: Path,
        output_path: Path,
        markdown_content: str,
        metadata: Optional[DocumentMetadata] = None,
        images: Optional[list[ImageInfo]] = None,
        pages_processed: int = 0,
        warnings: Optional[list[str]] = None,
    ) -> ConversionResult:
        """
        Create a successful conversion result.

        Args:
            source_path: Source file path.
            output_path: Output file path.
            markdown_content: The converted Markdown content.
            metadata: Extracted document metadata.
            images: List of extracted images.
            pages_processed: Number of pages processed.
            warnings: List of warning messages.

        Returns:
            A ConversionResult with success status.
        """
        return ConversionResult(
            source_path=source_path,
            output_path=output_path,
            status=ConversionStatus.SUCCESS,
            markdown_content=markdown_content,
            metadata=metadata,
            images=images or [],
            warnings=warnings or [],
            pages_processed=pages_processed,
        )

    def _create_error_result(
        self,
        source_path: Path,
        output_path: Path,
        errors: list[str],
        partial_content: Optional[str] = None,
    ) -> ConversionResult:
        """
        Create a failed or partial conversion result.

        Args:
            source_path: Source file path.
            output_path: Output file path.
            errors: List of error messages.
            partial_content: Partially converted content, if any.

        Returns:
            A ConversionResult with failed or partial status.
        """
        status = ConversionStatus.PARTIAL if partial_content else ConversionStatus.FAILED
        return ConversionResult(
            source_path=source_path,
            output_path=output_path,
            status=status,
            markdown_content=partial_content,
            errors=errors,
        )
