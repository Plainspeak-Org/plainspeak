DataSpeak: Natural Language Data Analysis
=====================================

.. note::
   DataSpeak is a planned feature for future releases of PlainSpeak. This documentation provides a preview of the functionality that will be available.

Overview
-------

DataSpeak extends PlainSpeak's natural language capabilities to data analysis, allowing you to query, analyze, and visualize data using plain English. It transforms natural language questions into SQL queries, data transformations, and visualizations.

Key Features
----------

- **Natural Language Queries**: Ask questions about your data in plain English
- **SQL Generation**: Automatically generate SQL queries from natural language
- **Data Visualization**: Create charts and graphs with simple commands
- **Data Exploration**: Explore and understand your data without SQL knowledge
- **Integration with Popular Data Formats**: CSV, Excel, SQLite, and more

How It Will Work
--------------

DataSpeak will follow a simple workflow:

1. **Initialize Data**: Point DataSpeak to your data sources
2. **Ask Questions**: Use natural language to query your data
3. **Review & Execute**: See the generated SQL, approve it, and get results
4. **Visualize**: Optionally create visualizations of your results

Example Usage
-----------

.. code-block:: text

   # Initialize data source
   > plainspeak init-data ./SalesData/*.csv

   # Ask questions in natural language
   > total revenue by region in 2024

   I'll calculate the total revenue by region for 2024.

   SQL Query:
   SELECT region, SUM(revenue) as total_revenue
   FROM sales
   WHERE year = 2024
   GROUP BY region
   ORDER BY total_revenue DESC;

   Execute? [Y/n/edit/visualize]: v

   Visualization type? [bar/pie/line]: bar

   [Bar chart showing revenue by region would be displayed]

Technical Implementation
---------------------

DataSpeak will be implemented as an extension to PlainSpeak's core architecture:

.. code-block:: text

   Component | Implementation | Purpose
   ----------|----------------|--------
   Intent Detection | Extended LLM prompt with data-query verbs | Recognizes data questions
   AST Structure | DataQuery(action, table, filters, measures, timeframe, output) | Structured format
   Renderer | Jinja templates that generate SQL | Transforms intent to queries
   Safety Layer | SQL parsing with sqlglot; read-only statements | Prevents data corruption
   Output Formatting | Pretty tables via rich; charts via matplotlib | Makes results accessible

Timeline
-------

DataSpeak is planned for inclusion in a future release of PlainSpeak. Stay tuned for updates on the development progress and release timeline.
