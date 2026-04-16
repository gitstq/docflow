"""Data models for DocFlow."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class DocumentFormat(str, Enum):
    """Supported document formats."""

    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    HTML = "html"
    HTM = "htm"
    TXT = "txt"
    MD = "md"
    MARKDOWN = "markdown"
    CSV = "csv"
    TSV = "tsv"
    JSON = "json"
    XML = "xml"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"


class ConversionStatus(str, Enum):
    """Conversion status codes."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DocumentMetadata:
    """Metadata extracted from a document."""

    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[List[str]] = field(default_factory=list)
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    file_size: Optional[int] = None
    custom_properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, list):
                    result[key] = value
                elif isinstance(value, dict):
                    result[key] = value
                else:
                    result[key] = value
        return result


@dataclass
class ImageInfo:
    """Information about an embedded image."""

    index: int
    original_format: str
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: Optional[int] = None
    alt_text: Optional[str] = None
    extracted_path: Optional[Path] = None
    ocr_text: Optional[str] = None


@dataclass
class ConversionOptions:
    """Options for document conversion."""

    # Output options
    output_dir: Optional[Path] = None
    output_filename: Optional[str] = None
    overwrite: bool = False

    # Content options
    extract_images: bool = True
    image_dir: Optional[str] = None
    preserve_structure: bool = True
    include_metadata: bool = True
    include_toc: bool = True

    # OCR options
    enable_ocr: bool = False
    ocr_language: str = "eng"
    ocr_dpi: int = 300

    # AI enhancement options
    enable_ai_summary: bool = False
    enable_ai_keywords: bool = False
    ai_model: Optional[str] = None
    ai_api_key: Optional[str] = None

    # Processing options
    batch_size: int = 10
    max_workers: int = 4
    timeout_seconds: int = 300
    retry_attempts: int = 3

    # Format-specific options
    pdf_extract_tables: bool = True
    pdf_merge_paragraphs: bool = True
    excel_sheet_pattern: Optional[str] = None
    html_ignore_links: bool = False
    html_ignore_images: bool = False

    def __post_init__(self) -> None:
        """Validate and normalize paths."""
        if self.output_dir is not None and isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)


@dataclass
class ConversionResult:
    """Result of a single document conversion."""

    source_path: Path
    output_path: Optional[Path]
    status: ConversionStatus
    markdown_content: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    images: List[ImageInfo] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    pages_processed: int = 0

    @property
    def success(self) -> bool:
        """Check if conversion was successful."""
        return self.status in (ConversionStatus.SUCCESS, ConversionStatus.PARTIAL)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "source_path": str(self.source_path),
            "output_path": str(self.output_path) if self.output_path else None,
            "status": self.status.value,
            "has_content": self.markdown_content is not None,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "image_count": len(self.images),
            "errors": self.errors,
            "warnings": self.warnings,
            "processing_time_seconds": self.processing_time_seconds,
            "pages_processed": self.pages_processed,
        }


@dataclass
class BatchConversionResult:
    """Result of a batch conversion operation."""

    results: List[ConversionResult] = field(default_factory=list)
    total_files: int = 0
    successful: int = 0
    partial: int = 0
    failed: int = 0
    skipped: int = 0
    total_processing_time: float = 0.0

    def add_result(self, result: ConversionResult) -> None:
        """Add a conversion result to the batch."""
        self.results.append(result)
        self.total_files += 1
        self.total_processing_time += result.processing_time_seconds

        if result.status == ConversionStatus.SUCCESS:
            self.successful += 1
        elif result.status == ConversionStatus.PARTIAL:
            self.partial += 1
        elif result.status == ConversionStatus.FAILED:
            self.failed += 1
        else:
            self.skipped += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert batch result to dictionary."""
        return {
            "total_files": self.total_files,
            "successful": self.successful,
            "partial": self.partial,
            "failed": self.failed,
            "skipped": self.skipped,
            "total_processing_time": round(self.total_processing_time, 2),
            "success_rate": (
                round((self.successful + self.partial) / self.total_files * 100, 1)
                if self.total_files > 0
                else 0.0
            ),
        }


@dataclass
class QualityReport:
    """Quality assessment report for conversion results."""

    result: ConversionResult
    completeness_score: float = 0.0
    formatting_score: float = 0.0
    content_preservation_score: float = 0.0
    overall_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def calculate_overall_score(self) -> None:
        """Calculate the overall quality score."""
        weights = {
            "completeness": 0.4,
            "formatting": 0.3,
            "content_preservation": 0.3,
        }
        self.overall_score = (
            weights["completeness"] * self.completeness_score
            + weights["formatting"] * self.formatting_score
            + weights["content_preservation"] * self.content_preservation_score
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "source": str(self.result.source_path),
            "completeness_score": round(self.completeness_score, 2),
            "formatting_score": round(self.formatting_score, 2),
            "content_preservation_score": round(self.content_preservation_score, 2),
            "overall_score": round(self.overall_score, 2),
            "issues": self.issues,
            "recommendations": self.recommendations,
        }
