"""HTML to Markdown converter."""

from pathlib import Path

from docflow.core.converters.base import BaseConverter
from docflow.core.models import DocumentMetadata

try:
    import html2text
    from bs4 import BeautifulSoup
    HAS_HTML_LIBS = True
except ImportError:
    HAS_HTML_LIBS = False


class HTMLConverter(BaseConverter):
    """Convert HTML documents to Markdown."""

    def convert(self, source_path: Path, output_path: Path):
        """Convert an HTML document to Markdown."""
        if not HAS_HTML_LIBS:
            return self._create_error_result(
                source_path,
                output_path,
                ["HTML libraries not installed. Run: pip install html2text beautifulsoup4"],
            )

        try:
            content = source_path.read_text(encoding="utf-8")
            soup = BeautifulSoup(content, "html.parser")

            # Extract title
            title = None
            if soup.title:
                title = soup.title.string

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()

            # Configure html2text
            h = html2text.HTML2Text()
            h.ignore_links = self.options.html_ignore_links
            h.ignore_images = self.options.html_ignore_images
            h.ignore_emphasis = False
            h.body_width = 0  # Don't wrap lines
            h.unicode_snob = True

            # Convert to Markdown
            markdown_content = h.handle(str(soup))

            metadata = DocumentMetadata(
                title=title,
                file_size=source_path.stat().st_size if source_path.exists() else None,
            )

            return self._create_success_result(
                source_path,
                output_path,
                markdown_content.strip(),
                metadata=metadata,
            )

        except Exception as e:
            return self._create_error_result(
                source_path, output_path, [f"HTML conversion error: {str(e)}"]
            )
