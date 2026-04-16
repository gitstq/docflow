"""Text file to Markdown converter."""

from pathlib import Path

from docflow.core.converters.base import BaseConverter
from docflow.core.models import DocumentMetadata


class TextConverter(BaseConverter):
    """Convert plain text files to Markdown."""

    SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".json", ".xml", ".text"}

    def convert(self, source_path: Path, output_path: Path):
        """Convert a text file to Markdown."""
        try:
            content = source_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = source_path.read_text(encoding="latin-1")
            except Exception as e:
                return self._create_error_result(
                    source_path, output_path, [f"Failed to read file: {str(e)}"]
                )

        # If it's already markdown, just return it
        if source_path.suffix.lower() in {".md", ".markdown"}:
            markdown_content = content
        elif source_path.suffix.lower() == ".json":
            markdown_content = self._format_json(content)
        elif source_path.suffix.lower() == ".xml":
            markdown_content = self._format_xml(content)
        else:
            markdown_content = self._format_text(content)

        metadata = DocumentMetadata(
            title=source_path.stem,
            file_size=source_path.stat().st_size if source_path.exists() else None,
        )

        return self._create_success_result(
            source_path,
            output_path,
            markdown_content,
            metadata=metadata,
        )

    def _format_text(self, content: str) -> str:
        """Format plain text as Markdown."""
        lines = content.split("\n")
        result = []
        in_paragraph = False

        for line in lines:
            stripped = line.strip()
            if stripped:
                if not in_paragraph:
                    result.append("")
                result.append(stripped)
                in_paragraph = True
            else:
                if in_paragraph:
                    result.append("")
                in_paragraph = False

        return "\n".join(result).strip()

    def _format_json(self, content: str) -> str:
        """Format JSON as Markdown code block."""
        import json
        try:
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            return f"```json\n{formatted}\n```"
        except json.JSONDecodeError:
            return f"```json\n{content}\n```"

    def _format_xml(self, content: str) -> str:
        """Format XML as Markdown code block."""
        import xml.dom.minidom as minidom
        try:
            parsed = minidom.parseString(content)
            formatted = parsed.toprettyxml(indent="  ")
            return f"```xml\n{formatted}\n```"
        except Exception:
            return f"```xml\n{content}\n```"
