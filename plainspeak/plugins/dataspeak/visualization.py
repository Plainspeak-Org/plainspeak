"""
DataSpeak Visualization Module

This module provides interactive data visualization capabilities for DataSpeak,
allowing users to visualize query results in various formats.
"""

import logging
import os
import tempfile
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt

    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    logging.warning("matplotlib not found, static visualizations will be limited")

try:
    import plotly.express as px
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    logging.warning("plotly not found, interactive visualizations will not be available")


class VisualizationError(Exception):
    """Exception raised when visualization fails."""


class DataVisualizer:
    """
    DataVisualizer provides methods for creating visualizations from DataFrames.

    It supports both static visualizations using matplotlib and interactive
    visualizations using plotly.
    """

    def __init__(self, interactive: bool = True, output_dir: Optional[str] = None):
        """
        Initialize the DataVisualizer.

        Args:
            interactive: Whether to use interactive visualizations when available.
            output_dir: Directory to save visualizations. If None, uses a temp directory.
        """
        self.interactive = interactive and HAS_PLOTLY
        self.logger = logging.getLogger("plainspeak.dataspeak.visualization")

        # Set output directory
        if output_dir:
            self.output_dir = Path(output_dir)
            os.makedirs(self.output_dir, exist_ok=True)
        else:
            self.output_dir = Path(tempfile.mkdtemp(prefix="plainspeak_viz_"))

        self.logger.info(f"Visualizations will be saved to {self.output_dir}")

    def autodetect_visualization(self, df: pd.DataFrame) -> str:
        """
        Automatically detect the best visualization type for the data.

        Args:
            df: The DataFrame to visualize.

        Returns:
            A string indicating the recommended visualization type.
        """
        # Get column types
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        num_cols = len(df.columns)
        len(df)

        # Simple rules for visualization recommendation
        if num_cols == 1:
            if df.columns[0] in numeric_cols:
                return "histogram"
            else:
                return "count"
        elif num_cols == 2:
            if len(numeric_cols) == 2:
                return "scatter"
            elif len(numeric_cols) == 1 and len(categorical_cols) == 1:
                if len(df[categorical_cols[0]].unique()) <= 10:
                    return "bar"
                else:
                    return "box"
            else:
                return "count"
        elif num_cols >= 3:
            if len(numeric_cols) >= 2:
                # If there's a date column, default to line
                if date_cols:
                    return "line"
                # If there's a categorical column with few values, use it for grouping
                elif categorical_cols and len(df[categorical_cols[0]].unique()) <= 8:
                    return "grouped_bar"
                else:
                    return "scatter_matrix"
            elif len(numeric_cols) == 1 and categorical_cols:
                if len(categorical_cols) == 1 and len(df[categorical_cols[0]].unique()) <= 15:
                    return "bar"
                else:
                    return "heatmap"
            else:
                return "table"

        return "table"  # Default to table view

    def create_visualization(
        self,
        df: pd.DataFrame,
        viz_type: Optional[str] = None,
        title: str = "Data Visualization",
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        color_col: Optional[str] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        """
        Create a visualization from a DataFrame.

        Args:
            df: The DataFrame to visualize.
            viz_type: The type of visualization to create. If None, auto-detected.
            title: The title for the visualization.
            x_col: Column to use for x-axis (if applicable).
            y_col: Column to use for y-axis (if applicable).
            color_col: Column to use for color encoding (if applicable).
            **kwargs: Additional arguments to pass to the visualization function.

        Returns:
            A tuple of (file_path, file_type) for the generated visualization.
        """
        # Auto-detect visualization type if not specified
        if not viz_type:
            viz_type = self.autodetect_visualization(df)

        self.logger.info(f"Creating {viz_type} visualization")

        # Select columns if not specified
        if not x_col and df.columns.size > 0:
            x_col = df.columns[0]

        if not y_col and df.columns.size > 1:
            y_col = df.columns[1]

        if not color_col and df.columns.size > 2:
            color_col = df.columns[2]

        # Create visualization based on type
        if self.interactive and HAS_PLOTLY:
            return self._create_interactive_viz(df, viz_type, title, x_col, y_col, color_col, **kwargs)
        elif HAS_MPL:
            return self._create_static_viz(df, viz_type, title, x_col, y_col, color_col, **kwargs)
        else:
            # Fallback to simple HTML table
            return self._create_html_table(df, title)

    def _create_interactive_viz(
        self,
        df: pd.DataFrame,
        viz_type: str,
        title: str,
        x_col: Optional[str],
        y_col: Optional[str],
        color_col: Optional[str],
        **kwargs,
    ) -> Tuple[str, str]:
        """Create an interactive visualization using plotly."""
        if not HAS_PLOTLY:
            raise VisualizationError("Plotly is required for interactive visualizations")

        filename = f"{self._sanitize_filename(title)}_{viz_type}.html"
        output_path = self.output_dir / filename

        fig = None

        try:
            # Create visualization based on type
            if viz_type == "table":
                fig = go.Figure(
                    data=[
                        go.Table(
                            header=dict(
                                values=list(df.columns),
                                fill_color="paleturquoise",
                                align="left",
                            ),
                            cells=dict(
                                values=[df[col] for col in df.columns],
                                fill_color="lavender",
                                align="left",
                            ),
                        )
                    ]
                )
                fig.update_layout(title=title)

            elif viz_type == "bar":
                if x_col and y_col:
                    fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
                else:
                    fig = px.bar(df, title=title)

            elif viz_type == "line":
                if x_col and y_col:
                    fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
                else:
                    fig = px.line(df, title=title)

            elif viz_type == "scatter":
                if x_col and y_col:
                    fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title)
                else:
                    fig = px.scatter(df, title=title)

            elif viz_type == "histogram":
                if x_col:
                    fig = px.histogram(df, x=x_col, color=color_col, title=title)
                else:
                    fig = px.histogram(df, title=title)

            elif viz_type == "box":
                if x_col and y_col:
                    fig = px.box(df, x=x_col, y=y_col, color=color_col, title=title)
                else:
                    fig = px.box(df, title=title)

            elif viz_type == "heatmap":
                # For heatmap, we need to reshape data if it's not already a matrix
                if df.select_dtypes(include=[np.number]).shape[1] >= 2:
                    # Try to use first categorical column for rows and second for columns
                    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                    if len(cat_cols) >= 2:
                        pivot_df = df.pivot_table(
                            index=cat_cols[0],
                            columns=cat_cols[1],
                            values=df.select_dtypes(include=[np.number]).columns[0],
                            aggfunc="mean",
                        )
                        fig = px.imshow(pivot_df, title=title)
                    else:
                        # Correlation matrix as fallback
                        corr_df = df.select_dtypes(include=[np.number]).corr()
                        fig = px.imshow(corr_df, title=f"{title} - Correlation Matrix")
                else:
                    raise VisualizationError("Heatmap requires at least two numeric columns")

            elif viz_type == "scatter_matrix":
                numeric_df = df.select_dtypes(include=[np.number])
                if numeric_df.shape[1] >= 2:
                    fig = px.scatter_matrix(
                        numeric_df,
                        dimensions=numeric_df.columns[:4],  # Limit to 4 dimensions
                        color=color_col,
                        title=title,
                    )
                else:
                    raise VisualizationError("Scatter matrix requires at least two numeric columns")

            elif viz_type == "grouped_bar":
                if not x_col or not y_col or not color_col:
                    # Try to autodetect appropriate columns
                    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

                    if len(cat_cols) >= 2 and num_cols:
                        x_col = cat_cols[0]
                        color_col = cat_cols[1]
                        y_col = num_cols[0]
                    else:
                        raise VisualizationError("Grouped bar chart requires categorical columns and a numeric column")

                fig = px.bar(df, x=x_col, y=y_col, color=color_col, barmode="group", title=title)

            elif viz_type == "pie":
                fig = px.pie(df, names=x_col, values=y_col, title=title)

            else:
                # Default to a table view
                fig = go.Figure(
                    data=[
                        go.Table(
                            header=dict(
                                values=list(df.columns),
                                fill_color="paleturquoise",
                                align="left",
                            ),
                            cells=dict(
                                values=[df[col] for col in df.columns],
                                fill_color="lavender",
                                align="left",
                            ),
                        )
                    ]
                )
                fig.update_layout(title=title)

            # Save the figure
            if fig:
                fig.write_html(str(output_path))
                return str(output_path), "html"

        except Exception as e:
            self.logger.error(f"Error creating interactive visualization: {str(e)}")
            # Fall back to static visualization
            return self._create_static_viz(df, viz_type, title, x_col, y_col, color_col, **kwargs)

        raise VisualizationError(f"Failed to create {viz_type} visualization")

    def _create_static_viz(
        self,
        df: pd.DataFrame,
        viz_type: str,
        title: str,
        x_col: Optional[str],
        y_col: Optional[str],
        color_col: Optional[str],
        **kwargs,
    ) -> Tuple[str, str]:
        """Create a static visualization using matplotlib."""
        if not HAS_MPL:
            raise VisualizationError("Matplotlib is required for static visualizations")

        filename = f"{self._sanitize_filename(title)}_{viz_type}.png"
        output_path = self.output_dir / filename

        try:
            plt.figure(figsize=(10, 6))
            plt.title(title)

            if viz_type == "bar":
                if x_col and y_col:
                    df.plot(kind="bar", x=x_col, y=y_col, ax=plt.gca())
                else:
                    df.plot(kind="bar", ax=plt.gca())

            elif viz_type == "line":
                if x_col and y_col:
                    df.plot(kind="line", x=x_col, y=y_col, ax=plt.gca())
                else:
                    df.plot(kind="line", ax=plt.gca())

            elif viz_type == "scatter":
                if x_col and y_col:
                    df.plot(kind="scatter", x=x_col, y=y_col, ax=plt.gca())
                else:
                    df.plot(
                        kind="scatter",
                        x=df.columns[0],
                        y=df.columns[1] if len(df.columns) > 1 else df.columns[0],
                        ax=plt.gca(),
                    )

            elif viz_type == "histogram":
                if x_col:
                    df[x_col].plot(kind="hist", ax=plt.gca())
                else:
                    df.iloc[:, 0].plot(kind="hist", ax=plt.gca())

            elif viz_type == "box":
                if x_col:
                    df.boxplot(column=x_col, ax=plt.gca())
                else:
                    df.boxplot(ax=plt.gca())

            elif viz_type == "pie":
                if x_col and y_col:
                    df.plot(kind="pie", y=y_col, labels=df[x_col], ax=plt.gca())
                else:
                    df.plot(kind="pie", y=df.columns[0], ax=plt.gca())

            elif viz_type == "heatmap":
                # Try to create a correlation heatmap as fallback
                try:
                    corr_df = df.select_dtypes(include=[np.number]).corr()
                    plt.imshow(corr_df, cmap="viridis")
                    plt.colorbar()
                    plt.xticks(range(len(corr_df.columns)), corr_df.columns, rotation=45)
                    plt.yticks(range(len(corr_df.columns)), corr_df.columns)
                except Exception as e:
                    self.logger.error(f"Error creating heatmap: {e}")
                    # Fall back to table
                    self._create_html_table(df, title)

            else:
                # Default to a basic table for unknown types
                return self._create_html_table(df, title)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300)
            plt.close()

            return str(output_path), "png"

        except Exception as e:
            self.logger.error(f"Error creating static visualization: {str(e)}")
            # Fall back to HTML table
            return self._create_html_table(df, title)

    def _create_html_table(self, df: pd.DataFrame, title: str) -> Tuple[str, str]:
        """Create a basic HTML table as a fallback visualization."""
        filename = f"{self._sanitize_filename(title)}_table.html"
        output_path = self.output_dir / filename

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
            {df.to_html(index=True)}
        </body>
        </html>
        """

        with open(output_path, "w") as f:
            f.write(html_content)

        return str(output_path), "html"

    def display_visualization(self, file_path: str) -> None:
        """
        Display a visualization in the default web browser or image viewer.

        Args:
            file_path: Path to the visualization file.
        """
        try:
            webbrowser.open(f"file://{file_path}")
        except Exception as e:
            self.logger.error(f"Error displaying visualization: {str(e)}")
            print(f"Visualization saved to {file_path}")

    def export_visualization(
        self,
        df: pd.DataFrame,
        format_type: str = "auto",
        output_path: Optional[str] = None,
        **viz_kwargs,
    ) -> str:
        """
        Export a visualization to a file.

        Args:
            df: The DataFrame to visualize.
            format_type: The output format ("auto", "html", "png", "svg", "pdf", "json").
            output_path: Path for the output file. If None, auto-generated.
            **viz_kwargs: Additional arguments to pass to create_visualization.

        Returns:
            Path to the exported file.
        """
        # Auto-detect format based on output_path if provided
        if output_path and format_type == "auto":
            ext = os.path.splitext(output_path)[1].lower()
            if ext:
                format_type = ext[1:]  # Remove the dot

        # Map auto to html for interactive, png for static
        if format_type == "auto":
            format_type = "html" if self.interactive and HAS_PLOTLY else "png"

        # Create visualization
        viz_type = viz_kwargs.pop("viz_type", None)
        file_path, file_type = self.create_visualization(df, viz_type, **viz_kwargs)

        # If format_type is the same as file_type, just return the file
        if format_type == file_type:
            if output_path:
                # Copy file to requested output path
                import shutil

                shutil.copy2(file_path, output_path)
                return output_path
            return file_path

        # Handle conversion if needed
        if format_type == "json":
            # Export data as JSON
            if not output_path:
                output_path = os.path.splitext(file_path)[0] + ".json"

            df.to_json(output_path, orient="records", indent=2)
            return output_path

        elif format_type in ["csv", "xlsx", "parquet"]:
            # Export data in specified format
            if not output_path:
                output_path = os.path.splitext(file_path)[0] + f".{format_type}"

            if format_type == "csv":
                df.to_csv(output_path, index=False)
            elif format_type == "xlsx":
                df.to_excel(output_path, index=False)
            elif format_type == "parquet":
                df.to_parquet(output_path, index=False)

            return output_path

        else:
            # For other conversions, we'd need additional libraries
            self.logger.warning(f"Conversion to {format_type} not supported. Using {file_type} instead.")
            return file_path

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename to be safe for filesystem."""
        # Replace unsafe characters
        safe_filename = "".join(c if c.isalnum() or c in "_- " else "_" for c in filename)
        # Trim and lowercase
        return safe_filename.strip().lower().replace(" ", "_")[:50]


# Singleton instance for convenience
default_visualizer = None


def get_default_visualizer() -> DataVisualizer:
    """Get the default visualizer instance, creating it if necessary."""
    global default_visualizer
    if default_visualizer is None:
        default_visualizer = DataVisualizer()
    return default_visualizer


def visualize_data(data: Union[pd.DataFrame, Dict[str, List[Any]], List[Dict[str, Any]]], **kwargs) -> Tuple[str, str]:
    """
    Convenience function to visualize data.

    Args:
        data: DataFrame or data that can be converted to DataFrame.
        **kwargs: Arguments to pass to create_visualization.

    Returns:
        A tuple of (file_path, file_type) for the generated visualization.
    """
    visualizer = get_default_visualizer()

    # Convert to DataFrame if needed
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    return visualizer.create_visualization(data, **kwargs)
