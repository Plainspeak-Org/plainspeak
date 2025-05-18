"""
DataSpeak Export Module

This module provides functionality for exporting query results and visualizations
to various formats.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

# Try to import optional export dependencies
try:
    pass

    HAS_EXCEL = True
except ImportError:
    HAS_EXCEL = False
    logging.warning("openpyxl not found, Excel export will not be available")

try:
    pass

    HAS_PARQUET = True
except ImportError:
    HAS_PARQUET = False
    logging.warning("pyarrow not found, Parquet export will not be available")

try:
    from tabulate import tabulate

    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    logging.warning("tabulate not found, pretty text tables will use pandas display")


class ExportError(Exception):
    """Exception raised when export operations fail."""


class DataExporter:
    """
    DataExporter provides methods for exporting data to various formats.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the DataExporter.

        Args:
            output_dir: Directory to save exports. If None, uses a temp directory.
        """
        self.logger = logging.getLogger("plainspeak.dataspeak.export")

        # Set output directory
        if output_dir:
            self.output_dir = Path(output_dir)
            os.makedirs(self.output_dir, exist_ok=True)
        else:
            self.output_dir = Path(tempfile.mkdtemp(prefix="plainspeak_export_"))

        self.logger.info(f"Exports will be saved to {self.output_dir}")

    def export_to_csv(self, data: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Export data to a CSV file.

        Args:
            data: The DataFrame to export.
            filename: Name for the output file. If None, auto-generated.

        Returns:
            Path to the exported file.
        """
        if filename is None:
            filename = "export_data.csv"

        output_path = self.output_dir / filename

        try:
            data.to_csv(output_path, index=False)
            return str(output_path)
        except Exception as e:
            raise ExportError(f"Error exporting to CSV: {str(e)}")

    def export_to_json(
        self,
        data: pd.DataFrame,
        filename: Optional[str] = None,
        orient: str = "records",
        indent: int = 2,
    ) -> str:
        """
        Export data to a JSON file.

        Args:
            data: The DataFrame to export.
            filename: Name for the output file. If None, auto-generated.
            orient: JSON structure orientation. Default is "records".
            indent: Number of spaces for indentation. Default is 2.

        Returns:
            Path to the exported file.
        """
        if filename is None:
            filename = "export_data.json"

        output_path = self.output_dir / filename

        try:
            data.to_json(output_path, orient=orient, indent=indent)
            return str(output_path)
        except Exception as e:
            raise ExportError(f"Error exporting to JSON: {str(e)}")

    def export_to_excel(self, data: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Export data to an Excel file.

        Args:
            data: The DataFrame to export.
            filename: Name for the output file. If None, auto-generated.

        Returns:
            Path to the exported file.
        """
        if not HAS_EXCEL:
            raise ExportError("Excel export requires openpyxl to be installed")

        if filename is None:
            filename = "export_data.xlsx"

        output_path = self.output_dir / filename

        try:
            data.to_excel(output_path, index=False, engine="openpyxl")
            return str(output_path)
        except Exception as e:
            raise ExportError(f"Error exporting to Excel: {str(e)}")

    def export_to_parquet(self, data: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Export data to a Parquet file.

        Args:
            data: The DataFrame to export.
            filename: Name for the output file. If None, auto-generated.

        Returns:
            Path to the exported file.
        """
        if not HAS_PARQUET:
            raise ExportError("Parquet export requires pyarrow to be installed")

        if filename is None:
            filename = "export_data.parquet"

        output_path = self.output_dir / filename

        try:
            data.to_parquet(output_path, index=False, engine="pyarrow")
            return str(output_path)
        except Exception as e:
            raise ExportError(f"Error exporting to Parquet: {str(e)}")

    def export_to_html(
        self,
        data: pd.DataFrame,
        filename: Optional[str] = None,
        title: str = "Data Export",
        include_styles: bool = True,
    ) -> str:
        """
        Export data to an HTML file.

        Args:
            data: The DataFrame to export.
            filename: Name for the output file. If None, auto-generated.
            title: Title for the HTML page.
            include_styles: Whether to include CSS styles. Default is True.

        Returns:
            Path to the exported file.
        """
        if filename is None:
            filename = "export_data.html"

        output_path = self.output_dir / filename

        try:
            if include_styles:
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{title}</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 20px;
                        }}
                        h1 {{
                            color: #333;
                        }}
                        table {{
                            border-collapse: collapse;
                            width: 100%;
                            margin-top: 20px;
                        }}
                        th, td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        th {{
                            background-color: #f2f2f2;
                        }}
                        tr:nth-child(even) {{
                            background-color: #f9f9f9;
                        }}
                    </style>
                </head>
                <body>
                    <h1>{title}</h1>
                    {data.to_html(index=False)}
                </body>
                </html>
                """

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
            else:
                data.to_html(output_path, index=False)

            return str(output_path)
        except Exception as e:
            raise ExportError(f"Error exporting to HTML: {str(e)}")

    def export_to_markdown(self, data: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Export data to a Markdown file.

        Args:
            data: The DataFrame to export.
            filename: Name for the output file. If None, auto-generated.

        Returns:
            Path to the exported file.
        """
        if filename is None:
            filename = "export_data.md"

        output_path = self.output_dir / filename

        try:
            if HAS_TABULATE:
                md_table = tabulate(data, headers="keys", tablefmt="pipe", showindex=False)
            else:
                # Fallback to pandas HTML to Markdown conversion (basic)
                md_table = "| " + " | ".join(data.columns) + " |\n"
                md_table += "| " + " | ".join(["---"] * len(data.columns)) + " |\n"

                for _, row in data.iterrows():
                    md_table += "| " + " | ".join([str(v) for v in row.values]) + " |\n"

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_table)

            return str(output_path)
        except Exception as e:
            raise ExportError(f"Error exporting to Markdown: {str(e)}")

    def export_to_latex(self, data: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Export data to a LaTeX file.

        Args:
            data: The DataFrame to export.
            filename: Name for the output file. If None, auto-generated.

        Returns:
            Path to the exported file.
        """
        if filename is None:
            filename = "export_data.tex"

        output_path = self.output_dir / filename

        try:
            if HAS_TABULATE:
                latex_table = tabulate(data, headers="keys", tablefmt="latex", showindex=False)
            else:
                # Use pandas to_latex method
                latex_table = data.to_latex(index=False)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(latex_table)

            return str(output_path)
        except Exception as e:
            raise ExportError(f"Error exporting to LaTeX: {str(e)}")

    def export_multiple_formats(
        self,
        data: pd.DataFrame,
        formats: List[str],
        base_filename: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Export data to multiple formats.

        Args:
            data: The DataFrame to export.
            formats: List of formats to export to ("csv", "json", "excel", "parquet", "html", "markdown", "latex").
            base_filename: Base name for output files without extension. If None, auto-generated.

        Returns:
            Dictionary mapping formats to file paths.
        """
        if base_filename is None:
            base_filename = "export_data"

        results = {}

        for fmt in formats:
            fmt = fmt.lower()
            filename = f"{base_filename}.{fmt}" if fmt != "excel" else f"{base_filename}.xlsx"

            try:
                if fmt == "csv":
                    results[fmt] = self.export_to_csv(data, filename)
                elif fmt == "json":
                    results[fmt] = self.export_to_json(data, filename)
                elif fmt == "excel":
                    results[fmt] = self.export_to_excel(data, filename)
                elif fmt == "parquet":
                    results[fmt] = self.export_to_parquet(data, filename)
                elif fmt == "html":
                    results[fmt] = self.export_to_html(data, filename)
                elif fmt == "markdown" or fmt == "md":
                    results[fmt] = self.export_to_markdown(data, filename)
                elif fmt == "latex" or fmt == "tex":
                    results[fmt] = self.export_to_latex(data, filename)
                else:
                    self.logger.warning(f"Unsupported format: {fmt}")
            except ExportError as e:
                self.logger.error(f"Error exporting to {fmt}: {str(e)}")

        return results

    def get_supported_formats(self) -> Dict[str, bool]:
        """
        Get a dictionary of supported export formats and their availability.

        Returns:
            Dictionary mapping format names to availability booleans.
        """
        return {
            "csv": True,
            "json": True,
            "excel": HAS_EXCEL,
            "parquet": HAS_PARQUET,
            "html": True,
            "markdown": True,
            "latex": True,
        }


# Singleton instance for convenience
default_exporter = None


def get_default_exporter() -> DataExporter:
    """Get the default exporter instance, creating it if necessary."""
    global default_exporter
    if default_exporter is None:
        default_exporter = DataExporter()
    return default_exporter


def export_data(
    data: Union[pd.DataFrame, Dict[str, List[Any]], List[Dict[str, Any]]],
    format_type: str = "csv",
    filename: Optional[str] = None,
) -> str:
    """
    Convenience function to export data to a file.

    Args:
        data: DataFrame or data that can be converted to DataFrame.
        format_type: Export format (csv, json, excel, parquet, html, markdown, latex).
        filename: Name for the output file. If None, auto-generated.

    Returns:
        Path to the exported file.
    """
    exporter = get_default_exporter()

    # Convert to DataFrame if needed
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    format_type = format_type.lower()

    if format_type == "csv":
        return exporter.export_to_csv(data, filename)
    elif format_type == "json":
        return exporter.export_to_json(data, filename)
    elif format_type == "excel":
        return exporter.export_to_excel(data, filename)
    elif format_type == "parquet":
        return exporter.export_to_parquet(data, filename)
    elif format_type == "html":
        return exporter.export_to_html(data, filename)
    elif format_type == "markdown" or format_type == "md":
        return exporter.export_to_markdown(data, filename)
    elif format_type == "latex" or format_type == "tex":
        return exporter.export_to_latex(data, filename)
    else:
        raise ValueError(f"Unsupported export format: {format_type}")
