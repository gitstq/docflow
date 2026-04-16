"""CSV/TSV to Markdown converter."""

import csv
from pathlib import Path

from docflow.core.converters.base import BaseConverter
from docflow.core.models import DocumentMetadata


class CSVConverter(BaseConverter):
    """Convert CSV/TSV files to Markdown."""

    def convert(self, source_path: Path, output_path: Path):
        """Convert a CSV/TSV file to Markdown."""
        try:
            # Detect delimiter
            delimiter = "\t" if source_path.suffix.lower() == ".tsv" else ","

            # Read CSV
            with open(source_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)

            if not rows:
                return self._create_success_result(
                    source_path,
                    output_path,
                    "*Empty file*",
                )

            # Convert to Markdown table
            markdown_content = self._format_table(rows)

            # Count statistics
            row_count = len(rows) - 1  # Exclude header
            col_count = len(rows[0]) if rows else 0

            metadata = DocumentMetadata(
                title=source_path.stem,
                file_size=source_path.stat().st_size if source_path.exists() else None,
                word_count=row_count,
            )

            return self._create_success_result(
                source_path,
                output_path,
                markdown_content,
                metadata=metadata,
            )

        except UnicodeDecodeError:
            # Try with latin-1
            try:
                with open(source_path, "r", encoding="latin-1", newline="") as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    rows = list(reader)
                markdown_content = self._format_table(rows)
                return self._create_success_result(
                    source_path, output_path, markdown_content
                )
            except Exception as e:
                return self._create_error_result(
                    source_path, output_path, [f"CSV read error: {str(e)}"]
                )
        except Exception as e:
            return self._create_error_result(
                source_path, output_path, [f"CSV conversion error: {str(e)}"]
            )

    def _format_table(self, rows: list[list[str]]) -> str:
        """Format rows as a Markdown table."""
        if not rows:
            return ""

        header = rows[0]
        separator = ["---"] * len(header)
        body = rows[1:]

        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(separator) + " |",
        ]
        for row in body:
            # Pad row if necessary
            while len(row) < len(header):
                row.append("")
            lines.append("| " + " | ".join(row[:len(header)]) + " |")

        return "\n".join(lines)
