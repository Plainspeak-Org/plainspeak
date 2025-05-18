# DataSpeak Plugin

The DataSpeak plugin is a powerful extension for PlainSpeak that transforms natural language queries into SQL, providing a seamless natural language interface to data analysis.

## Overview

DataSpeak enables users to query and visualize data using everyday language without needing to write SQL code. It provides:

- Natural language to SQL translation
- Data visualization capabilities
- Secure query execution
- Multiple export formats for results

## Modules

### Security Module (`security.py`)

The security module implements multiple layers of defense for SQL queries:

- SQL syntax validation
- Command whitelisting
- Query analysis for potentially dangerous operations
- Parameter sanitization

#### Security Levels

DataSpeak supports multiple security levels:

- **LOW**: Allows most operations with minimal checking
- **MEDIUM**: Blocks unsafe operations, allows modifications within constraints
- **HIGH**: Read-only mode, no modifications allowed
- **PARANOID**: Strict whitelist, parameter binding, full validation

#### Key Components

- `SQLSecurityChecker`: Main class for validating and sanitizing SQL queries
- `SecurityLevel`: Enum defining different security levels
- `is_safe_query()`: Helper function to quickly check query safety
- `sanitize_and_check_query()`: Sanitizes and validates a query in one step

### Visualization Module (`visualization.py`)

The visualization module provides interactive and static data visualization capabilities:

- Automatic detection of appropriate visualization types
- Support for various chart types (bar, line, scatter, pie, etc.)
- Interactive visualizations using Polly (when available)
- Static visualizations using various plotting libraries (fallback)

#### Key Features

- Automatic visualization type detection based on data characteristics
- Support for both interactive and static visualizations
- HTML output for compatibility across platforms
- Multiple chart types including:
  - Bar charts
  - Line charts
  - Scatter plots
  - Pie charts
  - Histograms
  - Heat maps
  - Box plots
  - And more

#### Main Components

- `DataVisualizer`: Core class for creating and displaying visualizations
- `visualize_data()`: Helper function for quick visualization of data
- Fallback mechanisms when visualization libraries are not available

### Export Module (`export.py`)

The export module enables exporting query results in various formats:

- CSV (Comma-Separated Values)
- JSON (JavaScript Object Notation)
- Excel (.xlsx)
- Parquet (columnar storage format)
- HTML (for web display)
- Markdown (for documentation)
- LaTeX (for academic papers)

#### Key Features

- Support for multiple export formats
- Graceful fallbacks when optional dependencies are missing
- Batch export to multiple formats
- Customizable export options

#### Main Components

- `DataExporter`: Core class for handling exports
- `export_data()`: Helper function for quick exports
- Format-specific export methods with appropriate options

## Usage Examples

### Querying Data

```
plainspeak query "Show me all sales from last month"
plainspeak ask "What were the top 5 products by revenue?"
plainspeak find "Customers who bought more than $1000 in the last quarter"
```

### Visualizing Data

```
plainspeak chart "Show sales trends over the last 12 months"
plainspeak visualize "Distribution of customer spending by region"
plainspeak plot "Compare product categories by monthly sales"
```

### Exporting Results

```
plainspeak export "Monthly sales data" to csv
plainspeak save "Customer list with contact details" as excel
plainspeak export "Product inventory" to json
```

## Configuration

DataSpeak can be configured through PlainSpeak's configuration system:

- Set default security level
- Configure visualization preferences
- Specify default export formats and locations

## Dependencies

- **Required**:
  - pandas (for data manipulation)
  - SQLite (embedded database)

- **Optional**:
  - Enhanced SQL parsing libraries
  - Visualization libraries for data plotting
  - Polly (for interactive visualizations)
  - Excel export utilities
  - Advanced data format libraries
  - tabulate (for pretty text tables)

## Integration with Other Plugins

DataSpeak works seamlessly with other PlainSpeak plugins:

- **File Plugin**: Load data from files
- **System Plugin**: Access system information as data
- **Network Plugin**: Download datasets from URLs

## Future Development

Planned enhancements for DataSpeak include:

- Support for additional database backends (PostgreSQL, MySQL, etc.)
- Machine learning integration for predictive analytics
- Natural language generation for explaining query results
- Enhanced visualization options and customizations
