"""Tests for DocFlow converter."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from docflow.core.converter import DocFlowConverter
from docflow.core.models import ConversionOptions, ConversionStatus, DocumentFormat


class TestDocFlowConverter:
    """Test cases for DocFlowConverter."""

    def test_get_supported_formats(self):
        """Test that supported formats are returned."""
        formats = DocFlowConverter.get_supported_formats()
        assert len(formats) > 0
        assert DocumentFormat.PDF in formats
        assert DocumentFormat.DOCX in formats

    def test_is_supported_pdf(self, tmp_path):
        """Test PDF format detection."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake pdf")
        assert DocFlowConverter.is_supported(pdf_file) is True

    def test_is_supported_docx(self, tmp_path):
        """Test DOCX format detection."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_bytes(b"PK fake docx")
        assert DocFlowConverter.is_supported(docx_file) is True

    def test_is_supported_unsupported(self, tmp_path):
        """Test unsupported format detection."""
        unknown_file = tmp_path / "test.xyz"
        unknown_file.write_text("unknown format")
        assert DocFlowConverter.is_supported(unknown_file) is False

    def test_convert_nonexistent_file(self, tmp_path):
        """Test conversion of non-existent file."""
        converter = DocFlowConverter()
        result = converter.convert(tmp_path / "nonexistent.pdf")

        assert result.status == ConversionStatus.FAILED
        assert "not found" in result.errors[0].lower()

    def test_convert_options_default(self):
        """Test default conversion options."""
        options = ConversionOptions()
        assert options.extract_images is True
        assert options.enable_ocr is False
        assert options.overwrite is False

    def test_convert_options_custom(self):
        """Test custom conversion options."""
        options = ConversionOptions(
            extract_images=False,
            enable_ocr=True,
            ocr_language="chi_sim",
            max_workers=8,
        )
        assert options.extract_images is False
        assert options.enable_ocr is True
        assert options.ocr_language == "chi_sim"
        assert options.max_workers == 8


class TestTextConverter:
    """Test cases for text file conversion."""

    def test_convert_txt_file(self, tmp_path):
        """Test plain text file conversion."""
        # Create test file
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Hello, World!\n\nThis is a test.", encoding="utf-8")

        converter = DocFlowConverter()
        result = converter.convert(txt_file)

        assert result.status == ConversionStatus.SUCCESS
        assert "Hello, World!" in result.markdown_content

    def test_convert_markdown_file(self, tmp_path):
        """Test markdown file conversion."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Title\n\nContent here.", encoding="utf-8")

        converter = DocFlowConverter()
        result = converter.convert(md_file)

        assert result.status == ConversionStatus.SUCCESS
        assert "# Title" in result.markdown_content

    def test_convert_json_file(self, tmp_path):
        """Test JSON file conversion."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}', encoding="utf-8")

        converter = DocFlowConverter()
        result = converter.convert(json_file)

        assert result.status == ConversionStatus.SUCCESS
        assert "```json" in result.markdown_content


class TestCSVConverter:
    """Test cases for CSV file conversion."""

    def test_convert_csv_file(self, tmp_path):
        """Test CSV file conversion."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Age\nAlice,30\nBob,25", encoding="utf-8")

        converter = DocFlowConverter()
        result = converter.convert(csv_file)

        assert result.status == ConversionStatus.SUCCESS
        assert "| Name | Age |" in result.markdown_content

    def test_convert_tsv_file(self, tmp_path):
        """Test TSV file conversion."""
        tsv_file = tmp_path / "test.tsv"
        tsv_file.write_text("Name\tAge\nAlice\t30", encoding="utf-8")

        converter = DocFlowConverter()
        result = converter.convert(tsv_file)

        assert result.status == ConversionStatus.SUCCESS


class TestBatchConversion:
    """Test cases for batch conversion."""

    def test_batch_convert_multiple_files(self, tmp_path):
        """Test batch conversion of multiple files."""
        # Create test files
        (tmp_path / "file1.txt").write_text("Content 1")
        (tmp_path / "file2.txt").write_text("Content 2")
        (tmp_path / "file3.txt").write_text("Content 3")

        converter = DocFlowConverter()
        result = converter.convert_directory(tmp_path, recursive=False)

        assert result.total_files == 3
        assert result.successful == 3

    def test_batch_convert_with_unsupported_files(self, tmp_path):
        """Test batch conversion skips unsupported files."""
        (tmp_path / "supported.txt").write_text("Content")
        (tmp_path / "unsupported.xyz").write_text("Unknown")

        converter = DocFlowConverter()
        result = converter.convert_directory(tmp_path, recursive=False)

        assert result.total_files == 1
        assert result.successful == 1
