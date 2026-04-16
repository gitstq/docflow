"""
DocFlow - High-performance document conversion and intelligent processing engine.

A powerful CLI tool for converting various document formats to Markdown,
with support for batch processing, OCR, metadata extraction, and AI enhancement.
"""

__version__ = "1.0.0"
__author__ = "DocFlow Team"
__license__ = "MIT"

from docflow.core.converter import DocFlowConverter
from docflow.core.models import ConversionResult, ConversionOptions

__all__ = [
    "DocFlowConverter",
    "ConversionResult",
    "ConversionOptions",
    "__version__",
]
