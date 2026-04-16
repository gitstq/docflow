"""CLI entry point for DocFlow."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.tree import Tree

from docflow import __version__
from docflow.core.converter import DocFlowConverter
from docflow.core.models import ConversionOptions
from docflow.utils.logger import get_logger, set_log_level

console = Console()
logger = get_logger()


@click.group()
@click.version_option(version=__version__, prog_name="docflow")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.option("--log-file", type=click.Path(), help="Path to log file")
def main(verbose: bool, quiet: bool, log_file: Optional[str]) -> None:
    """
    DocFlow - High-performance document conversion and intelligent processing engine.

    Convert various document formats to Markdown with support for batch processing,
    OCR, metadata extraction, and AI enhancement.
    """
    if verbose:
        set_log_level(20)  # DEBUG
    elif quiet:
        set_log_level(40)  # ERROR


@main.command()
@click.argument("source", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file or directory")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["markdown", "md"]),
    default="markdown",
    help="Output format",
)
@click.option("--extract-images", is_flag=True, default=True, help="Extract images from documents")
@click.option("--enable-ocr", is_flag=True, help="Enable OCR for images and scanned PDFs")
@click.option("--ocr-language", default="eng", help="OCR language (default: eng)")
@click.option("--include-metadata", is_flag=True, default=True, help="Include metadata in output")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output files")
def convert(
    source: str,
    output: Optional[str],
    output_format: str,
    extract_images: bool,
    enable_ocr: bool,
    ocr_language: str,
    include_metadata: bool,
    overwrite: bool,
) -> None:
    """
    Convert a document to Markdown.

    SOURCE can be a file or directory path.
    """
    source_path = Path(source)

    options = ConversionOptions(
        output_dir=Path(output) if output and Path(output).is_dir() else None,
        overwrite=overwrite,
        extract_images=extract_images,
        enable_ocr=enable_ocr,
        ocr_language=ocr_language,
        include_metadata=include_metadata,
    )

    converter = DocFlowConverter(options)

    with console.status("[bold green]Converting...") as status:
        if source_path.is_file():
            output_path = Path(output) if output else None
            result = converter.convert(source_path, output_path)

            if result.success:
                console.print(f"[green]OK[/green] Converted: {result.source_path}")
                console.print(f"  Output: {result.output_path}")
                console.print(f"  Time: {result.processing_time_seconds:.2f}s")

                if result.metadata:
                    console.print(f"  Pages: {result.metadata.page_count or 'N/A'}")

                if result.warnings:
                    for warning in result.warnings:
                        console.print(f"  [yellow]Warning:[/yellow] {warning}")
            else:
                console.print(f"[red]FAIL[/red] Failed: {result.source_path}")
                for error in result.errors:
                    console.print(f"  [red]Error:[/red] {error}")
                sys.exit(1)

        elif source_path.is_dir():
            output_dir = Path(output) if output else None
            batch_result = converter.convert_directory(source_path, output_dir=output_dir)

            # Display summary
            console.print()
            summary_table = Table(title="Conversion Summary")
            summary_table.add_column("Status", style="bold")
            summary_table.add_column("Count", justify="right")

            summary_table.add_row("[green]Successful[/green]", str(batch_result.successful))
            summary_table.add_row("[yellow]Partial[/yellow]", str(batch_result.partial))
            summary_table.add_row("[red]Failed[/red]", str(batch_result.failed))
            summary_table.add_row("[dim]Skipped[/dim]", str(batch_result.skipped))
            summary_table.add_row("[bold]Total[/bold]", str(batch_result.total_files))

            console.print(summary_table)
            console.print(f"\nTotal time: {batch_result.total_processing_time:.2f}s")

        else:
            console.print(f"[red]Error:[/red] Invalid source path: {source_path}")
            sys.exit(1)


@main.command()
@click.argument("source", type=click.Path(exists=True))
@click.option("--recursive", "-r", is_flag=True, help="Process directories recursively")
@click.option("--pattern", "-p", default="*", help="File pattern to match")
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory for converted files")
@click.option(
    "--workers",
    "-w",
    default=4,
    help="Number of parallel workers",
)
@click.option("--enable-ocr", is_flag=True, help="Enable OCR for images")
@click.option("--overwrite", is_flag=True, help="Overwrite existing files")
def batch(
    source: str,
    recursive: bool,
    pattern: str,
    output_dir: Optional[str],
    workers: int,
    enable_ocr: bool,
    overwrite: bool,
) -> None:
    """
    Batch convert multiple documents.

    SOURCE can be a directory or a file containing paths (one per line).
    """
    source_path = Path(source)

    options = ConversionOptions(
        output_dir=Path(output_dir) if output_dir else None,
        overwrite=overwrite,
        enable_ocr=enable_ocr,
        max_workers=workers,
    )

    converter = DocFlowConverter(options)

    if source_path.is_dir():
        console.print(f"[bold]Scanning directory:[/bold] {source_path}")
        if recursive:
            console.print("[dim]  (recursive)[/dim]")

        result = converter.convert_directory(
            source_path,
            recursive=recursive,
            pattern=pattern,
            output_dir=Path(output_dir) if output_dir else None,
        )

    elif source_path.is_file() and source_path.suffix == ".txt":
        # Read list of files
        files = [
            Path(line.strip())
            for line in source_path.read_text().splitlines()
            if line.strip()
        ]
        console.print(f"[bold]Processing {len(files)} files from list[/bold]")

        result = converter.convert_batch(
            files,
            output_dir=Path(output_dir) if output_dir else None,
        )

    else:
        console.print(f"[red]Error:[/red] Invalid source: {source_path}")
        sys.exit(1)

    # Display results
    console.print()

    # Success table
    if result.successful + result.partial > 0:
        success_table = Table(title="Successful Conversions")
        success_table.add_column("File", style="green")
        success_table.add_column("Status")
        success_table.add_column("Time", justify="right")

        for r in result.results:
            if r.success:
                status = "[green]OK[/green]" if r.status.value == "success" else "[yellow]PARTIAL[/yellow]"
                success_table.add_row(
                    r.source_path.name,
                    status,
                    f"{r.processing_time_seconds:.2f}s",
                )

        console.print(success_table)

    # Errors table
    if result.failed > 0:
        console.print()
        error_table = Table(title="Failed Conversions")
        error_table.add_column("File", style="red")
        error_table.add_column("Error")

        for r in result.results:
            if not r.success:
                error_msg = r.errors[0] if r.errors else "Unknown error"
                error_table.add_row(r.source_path.name, error_msg[:50])

        console.print(error_table)

    # Summary
    console.print()
    console.print(f"[bold]Total:[/bold] {result.total_files} files")
    console.print(f"[bold]Time:[/bold] {result.total_processing_time:.2f}s")
    console.print(f"[bold]Success rate:[/bold] {result.to_dict()['success_rate']}%")


@main.command()
def formats() -> None:
    """List all supported document formats."""
    console.print("\n[bold]Supported Document Formats:[/bold]\n")

    formats_list = DocFlowConverter.get_supported_formats()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Format", style="cyan")
    table.add_column("Extensions")

    format_extensions = {
        "PDF": ".pdf",
        "Word": ".docx, .doc",
        "PowerPoint": ".pptx, .ppt",
        "Excel": ".xlsx, .xls",
        "HTML": ".html, .htm",
        "Text": ".txt, .md, .markdown",
        "Data": ".csv, .tsv, .json, .xml",
        "Image": ".png, .jpg, .jpeg, .gif, .bmp, .tiff, .webp",
    }

    for format_name, extensions in format_extensions.items():
        table.add_row(format_name, extensions)

    console.print(table)
    console.print()


@main.command()
@click.argument("source", type=click.Path(exists=True))
def info(source: str) -> None:
    """Display information about a document."""
    source_path = Path(source)

    if not DocFlowConverter.is_supported(source_path):
        console.print(f"[red]Error:[/red] Unsupported format: {source_path.suffix}")
        sys.exit(1)

    converter = DocFlowConverter()
    result = converter.convert(source_path)

    if result.metadata:
        console.print(f"\n[bold]Document Information:[/bold]\n")

        info_tree = Tree(f"[bold]{source_path.name}[/bold]")

        if result.metadata.title:
            info_tree.add(f"[cyan]Title:[/cyan] {result.metadata.title}")
        if result.metadata.author:
            info_tree.add(f"[cyan]Author:[/cyan] {result.metadata.author}")
        if result.metadata.subject:
            info_tree.add(f"[cyan]Subject:[/cyan] {result.metadata.subject}")
        if result.metadata.page_count:
            info_tree.add(f"[cyan]Pages:[/cyan] {result.metadata.page_count}")
        if result.metadata.word_count:
            info_tree.add(f"[cyan]Words:[/cyan] {result.metadata.word_count}")
        if result.metadata.creation_date:
            info_tree.add(f"[cyan]Created:[/cyan] {result.metadata.creation_date}")
        if result.metadata.modification_date:
            info_tree.add(f"[cyan]Modified:[/cyan] {result.metadata.modification_date}")
        if result.metadata.file_size:
            size_kb = result.metadata.file_size / 1024
            info_tree.add(f"[cyan]Size:[/cyan] {size_kb:.1f} KB")

        console.print(info_tree)
        console.print()
    else:
        console.print("[yellow]No metadata available[/yellow]")


if __name__ == "__main__":
    main()
