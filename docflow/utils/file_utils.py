"""File utility functions."""

import hashlib
from pathlib import Path
from typing import Optional

from docflow.core.models import DocumentFormat


def detect_format(file_path: Path) -> DocumentFormat:
    """
    Detect the document format from a file path.

    Args:
        file_path: Path to the file.

    Returns:
        The detected DocumentFormat.

    Raises:
        ValueError: If the format is not supported.
    """
    suffix = file_path.suffix.lower().lstrip(".")

    # Handle compound extensions
    if suffix == "gz":
        # Handle .tar.gz
        stem_suffix = file_path.stem.split(".")[-1].lower()
        if stem_suffix == "tar":
            raise ValueError(f"Unsupported format: tar.gz")

    # Map extensions to formats
    extension_map = {
        "pdf": DocumentFormat.PDF,
        "docx": DocumentFormat.DOCX,
        "doc": DocumentFormat.DOCX,  # Legacy Word format
        "pptx": DocumentFormat.PPTX,
        "ppt": DocumentFormat.PPTX,  # Legacy PowerPoint
        "xlsx": DocumentFormat.XLSX,
        "xls": DocumentFormat.XLSX,  # Legacy Excel
        "html": DocumentFormat.HTML,
        "htm": DocumentFormat.HTM,
        "txt": DocumentFormat.TXT,
        "md": DocumentFormat.MD,
        "markdown": DocumentFormat.MARKDOWN,
        "csv": DocumentFormat.CSV,
        "tsv": DocumentFormat.TSV,
        "json": DocumentFormat.JSON,
        "xml": DocumentFormat.XML,
        "png": DocumentFormat.PNG,
        "jpg": DocumentFormat.JPG,
        "jpeg": DocumentFormat.JPEG,
        "gif": DocumentFormat.GIF,
        "bmp": DocumentFormat.BMP,
        "tiff": DocumentFormat.TIFF,
        "tif": DocumentFormat.TIFF,
        "webp": DocumentFormat.WEBP,
    }

    if suffix not in extension_map:
        raise ValueError(f"Unsupported file format: .{suffix}")

    return extension_map[suffix]


def ensure_dir(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory.

    Returns:
        The path object.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Calculate the hash of a file.

    Args:
        file_path: Path to the file.
        algorithm: Hash algorithm to use (sha256, md5, etc.).

    Returns:
        The hex digest of the file hash.
    """
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def get_unique_filename(directory: Path, base_name: str, suffix: str = "") -> Path:
    """
    Generate a unique filename in a directory.

    Args:
        directory: Target directory.
        base_name: Base filename without extension.
        suffix: File extension (with dot).

    Returns:
        A unique file path.
    """
    candidate = directory / f"{base_name}{suffix}"
    counter = 1

    while candidate.exists():
        candidate = directory / f"{base_name}_{counter}{suffix}"
        counter += 1

    return candidate


def safe_filename(name: str) -> str:
    """
    Convert a string to a safe filename.

    Args:
        name: The input string.

    Returns:
        A safe filename string.
    """
    import re
    # Replace invalid characters with underscores
    safe = re.sub(r'[<>:"/\\|?*]', "_", name)
    # Remove leading/trailing spaces and dots
    safe = safe.strip(" .")
    # Collapse multiple underscores
    safe = re.sub(r"_+", "_", safe)
    return safe or "unnamed"


def read_file_with_encoding(
    file_path: Path, fallback_encodings: Optional[list[str]] = None
) -> tuple[str, str]:
    """
    Read a file trying multiple encodings.

    Args:
        file_path: Path to the file.
        fallback_encodings: List of encodings to try.

    Returns:
        Tuple of (content, encoding_used).
    """
    encodings = fallback_encodings or ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            content = file_path.read_text(encoding=encoding)
            return content, encoding
        except UnicodeDecodeError:
            continue

    # Last resort: read as binary and decode with errors ignored
    content = file_path.read_bytes().decode("utf-8", errors="ignore")
    return content, "utf-8-ignore"
