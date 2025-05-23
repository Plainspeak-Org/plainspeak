# Advanced Plugin Development Tutorial

This tutorial guides you through creating sophisticated PlainSpeak plugins with advanced features, real-world examples, and best practices.

## Prerequisites

Before starting this tutorial, make sure you:

- Have read the [Creating PlainSpeak Plugins](creating_plugins.md) guide
- Understand basic plugin development concepts
- Are familiar with Python and Jinja2 templates
- Have PlainSpeak installed and configured

## Building a Context-Aware Plugin

One of the most powerful features of advanced plugins is their ability to maintain state and be aware of context. Let's build a project management plugin that remembers the current project and adapts commands accordingly.

### ProjectManager Plugin

```python
from pathlib import Path
import os
import json
from typing import Dict, Any, Optional, List, Tuple

from plainspeak.plugins.base import Plugin, registry
from plainspeak.core.context import get_session_context, update_session_context

class ProjectManagerPlugin(Plugin):
    def __init__(self):
        super().__init__(
            name="project-manager",
            description="Manage development projects with context awareness",
            version="1.0.0"
        )
        self.config_dir = Path(os.path.expanduser("~/.config/plainspeak/project_manager"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.projects_file = self.config_dir / "projects.json"
        self._load_projects()

    def get_verbs(self):
        return [
            "project", "switch-project", "list-projects", "create-project",
            "delete-project", "add-task", "complete-task", "list-tasks",
            "project-status", "set-deadline"
        ]

    def _load_projects(self):
        """Load projects from disk."""
        if self.projects_file.exists():
            with open(self.projects_file, 'r') as f:
                self.projects = json.load(f)
        else:
            self.projects = {}
            self._save_projects()

    def _save_projects(self):
        """Save projects to disk."""
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=2)

    def _get_current_project(self) -> Optional[str]:
        """Get the current project from context."""
        context = get_session_context()
        return context.get("current_project")

    def _set_current_project(self, project_name: str):
        """Set the current project in context."""
        context = get_session_context()
        context["current_project"] = project_name
        update_session_context(context)

    def generate_command(self, verb, args):
        """Generate a command based on verb and arguments."""
        if verb == "project":
            # Just show current project or info about a specific project
            project_name = args.get("project_name") or self._get_current_project()
            if not project_name:
                return "echo 'No project currently selected. Use switch-project to select one.'"

            if project_name not in self.projects:
                return f"echo 'Project {project_name} does not exist.'"

            project_info = self.projects[project_name]
            return f"""
                echo 'Project: {project_name}'
                echo 'Path: {project_info.get("path", "Not set")}'
                echo 'Tasks: {len(project_info.get("tasks", []))}'
                echo 'Deadline: {project_info.get("deadline", "None")}'
            """

        elif verb == "switch-project":
            project_name = args.get("project_name")
            if not project_name:
                return "echo 'Please specify a project name.'"

            if project_name not in self.projects:
                return f"echo 'Project {project_name} does not exist.'"

            self._set_current_project(project_name)
            project_path = self.projects[project_name].get("path")

            if project_path:
                return f"""
                    echo 'Switched to project: {project_name}'
                    cd {project_path}
                """
            else:
                return f"echo 'Switched to project: {project_name}'"

        elif verb == "list-projects":
            if not self.projects:
                return "echo 'No projects found.'"

            current = self._get_current_project()
            project_list = "\n".join([
                f"{name} {'(current)' if name == current else ''}"
                for name in self.projects.keys()
            ])

            return f"""
                echo 'Projects:'
                echo '{project_list}'
            """

        elif verb == "create-project":
            project_name = args.get("project_name")
            if not project_name:
                return "echo 'Please specify a project name.'"

            if project_name in self.projects:
                return f"echo 'Project {project_name} already exists.'"

            path = args.get("path", os.getcwd())

            self.projects[project_name] = {
                "path": path,
                "tasks": [],
                "deadline": None
            }

            self._save_projects()
            self._set_current_project(project_name)

            return f"""
                echo 'Created project: {project_name}'
                echo 'Path: {path}'
            """

        # Implement other verbs (add-task, complete-task, etc.)
        # ...

    def execute_command(self, verb, args, command):
        """For certain verbs, execute custom logic instead of shell commands."""
        if verb == "add-task":
            return self._add_task(args)
        elif verb == "complete-task":
            return self._complete_task(args)
        elif verb == "list-tasks":
            return self._list_tasks(args)

        # For other verbs, let the default execution happen
        return None

    def _add_task(self, args):
        """Add a task to the current project."""
        project_name = args.get("project_name") or self._get_current_project()
        if not project_name or project_name not in self.projects:
            return "No valid project selected."

        task = args.get("task")
        if not task:
            return "Please specify a task description."

        priority = args.get("priority", "normal")

        self.projects[project_name]["tasks"].append({
            "description": task,
            "completed": False,
            "priority": priority,
            "id": len(self.projects[project_name]["tasks"]) + 1
        })

        self._save_projects()
        return f"Added task to {project_name}: {task} (priority: {priority})"

    # Implement _complete_task and _list_tasks methods
    # ...

# Register the plugin
registry.register(ProjectManagerPlugin())
```

## Plugin with Custom UI

Let's create a plugin that generates rich output using libraries like `rich` for terminal UI or even basic HTML rendering for more complex visualization.

### DataVisualizerPlugin

```python
from plainspeak.plugins.base import Plugin, registry
import json
import tempfile
import webbrowser
import os
from pathlib import Path

# Try to import optional dependencies
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

class DataVisualizerPlugin(Plugin):
    def __init__(self):
        super().__init__(
            name="data-visualizer",
            description="Visualize data in terminal or browser",
            version="1.0.0"
        )
        self.console = Console() if HAS_RICH else None

    def get_verbs(self):
        return [
            "visualize", "display-json", "render-table", "plot-data",
            "chart", "show-stats"
        ]

    def generate_command(self, verb, args):
        """For this plugin, we'll return marker commands that our execute_command will handle."""
        if verb == "visualize" or verb == "display-json":
            file_path = args.get("file")
            if not file_path:
                return "echo 'Please specify a file to visualize.'"

            # Return a command that simply indicates what we're doing
            # Our execute_command will catch this and handle the real work
            return f"echo 'Visualizing data from {file_path}...'"

        elif verb in ["render-table", "plot-data", "chart", "show-stats"]:
            # Similar pattern for other verbs
            return f"echo 'Executing {verb} with {json.dumps(args)}...'"

        return None

    def execute_command(self, verb, args, command):
        """Handle the actual data visualization."""
        if verb == "display-json":
            return self._display_json(args.get("file"))

        elif verb == "render-table":
            return self._render_table(
                args.get("file"),
                args.get("columns"),
                args.get("title", "Data Table")
            )

        elif verb == "chart" or verb == "plot-data":
            return self._generate_chart(
                args.get("file"),
                args.get("type", "bar"),
                args.get("x_column"),
                args.get("y_column"),
                args.get("title", "Data Chart")
            )

        # Let default execution happen for unhandled verbs
        return None

    def _display_json(self, file_path):
        """Display a JSON file in a pretty format."""
        if not file_path or not os.path.exists(file_path):
            return f"File not found: {file_path}"

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            if HAS_RICH:
                self.console.print_json(data=data)
                return "JSON data displayed with rich formatting."
            else:
                # Fallback to simple pretty printing
                return json.dumps(data, indent=2)

        except Exception as e:
            return f"Error processing JSON file: {str(e)}"

    def _render_table(self, file_path, columns=None, title="Data Table"):
        """Render data as a table."""
        if not file_path or not os.path.exists(file_path):
            return f"File not found: {file_path}"

        try:
            # Try to load data based on file extension
            if file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
            elif file_path.endswith('.csv'):
                # We'll need pandas for this, but let's keep it simple
                return "CSV support requires pandas. Please convert to JSON."
            else:
                return "Unsupported file format. Use JSON or CSV."

            # For simplicity, assume data is a list of dictionaries
            if not isinstance(data, list):
                return "Data must be a list of records."

            if not data:
                return "No data found in file."

            # If columns not specified, use all keys from the first record
            if not columns:
                columns = list(data[0].keys())

            if HAS_RICH:
                table = Table(title=title)
                for column in columns:
                    table.add_column(column)

                for record in data:
                    table.add_row(*[str(record.get(col, "")) for col in columns])

                self.console.print(table)
                return "Table rendered with rich formatting."
            else:
                # Fallback to simple table rendering
                result = [title, "-" * len(title)]
                result.append(" | ".join(columns))
                result.append("-" * len(result[-1]))

                for record in data:
                    result.append(" | ".join([str(record.get(col, "")) for col in columns]))

                return "\n".join(result)

        except Exception as e:
            return f"Error rendering table: {str(e)}"

    def _generate_chart(self, file_path, chart_type, x_column, y_column, title):
        """Generate a chart using HTML and open in browser."""
        if not file_path or not os.path.exists(file_path):
            return f"File not found: {file_path}"

        try:
            # Load data
            if file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
            else:
                return "Unsupported file format. Use JSON."

            # For simplicity, we'll generate a basic HTML chart with JavaScript
            # In a real plugin, you might use matplotlib, plotly, or other libraries

            # Extract data for the chart
            if not x_column or not y_column:
                return "Please specify x and y columns for the chart."

            x_values = [record.get(x_column, "") for record in data]
            y_values = [record.get(y_column, 0) for record in data]

            # Generate a simple HTML file with a chart
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title}</title>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head>
            <body>
                <div style="width: 800px; margin: 0 auto;">
                    <canvas id="chart"></canvas>
                </div>
                <script>
                    const ctx = document.getElementById('chart').getContext('2d');
                    new Chart(ctx, {
                        type: '{chart_type}',
                        data: {
                            labels: {json.dumps(x_values)},
                            datasets: [{
                                label: '{y_column}',
                                data: {json.dumps(y_values)},
                                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                borderColor: 'rgba(75, 192, 192, 1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                title: {
                                    display: true,
                                    text: '{title}'
                                }
                            }
                        }
                    });
                </script>
            </body>
            </html>
            """

            # Write to a temporary file and open it in the default browser
            fd, path = tempfile.mkstemp(suffix=".html")
            with os.fdopen(fd, 'w') as f:
                f.write(html)

            webbrowser.open(f"file://{path}")
            return f"Chart opened in your default web browser. Temporary file: {path}"

        except Exception as e:
            return f"Error generating chart: {str(e)}"

# Register the plugin
registry.register(DataVisualizerPlugin())
```

## Creating an API Integration Plugin

Let's create a plugin that interfaces with external APIs, complete with authentication, request handling, and response parsing.

### WeatherAPIPlugin

```python
from plainspeak.plugins.base import Plugin, registry
import os
import json
import tempfile
from datetime import datetime
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

class WeatherAPIPlugin(Plugin):
    def __init__(self):
        super().__init__(
            name="weather-api",
            description="Get weather information from OpenWeatherMap API",
            version="1.0.0"
        )
        # API key would normally come from the config
        self.api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_verbs(self):
        return [
            "weather", "forecast", "temperature", "humidity",
            "wind", "sunrise-sunset", "uv-index"
        ]

    def generate_command(self, verb, args):
        """Generate a placeholder command for API calls."""
        location = args.get("location", "")
        if not location:
            return "echo 'Please specify a location.'"

        # For API calls, we'll use placeholders that our execute_command will handle
        return f"echo 'Fetching {verb} data for {location}...'"

    def execute_command(self, verb, args, command):
        """Execute API calls instead of shell commands."""
        if not self.api_key:
            return "OpenWeatherMap API key not set. Please set the OPENWEATHERMAP_API_KEY environment variable."

        location = args.get("location", "")
        if not location:
            return "Please specify a location."

        if verb == "weather":
            return self._get_current_weather(location, args.get("units", "metric"))

        elif verb == "forecast":
            days = args.get("days", 5)
            return self._get_forecast(location, days, args.get("units", "metric"))

        elif verb == "temperature":
            weather_data = self._fetch_weather_data(location, args.get("units", "metric"))
            if isinstance(weather_data, str):  # Error message
                return weather_data

            temp = weather_data.get("main", {}).get("temp")
            feels_like = weather_data.get("main", {}).get("feels_like")

            unit_symbol = "°C" if args.get("units", "metric") == "metric" else "°F"
            return f"Temperature in {location}: {temp}{unit_symbol} (feels like {feels_like}{unit_symbol})"

        elif verb == "humidity":
            weather_data = self._fetch_weather_data(location, args.get("units", "metric"))
            if isinstance(weather_data, str):  # Error message
                return weather_data

            humidity = weather_data.get("main", {}).get("humidity")
            return f"Humidity in {location}: {humidity}%"

        elif verb == "wind":
            weather_data = self._fetch_weather_data(location, args.get("units", "metric"))
            if isinstance(weather_data, str):  # Error message
                return weather_data

            wind_speed = weather_data.get("wind", {}).get("speed")
            wind_direction = weather_data.get("wind", {}).get("deg")

            # Convert degrees to cardinal direction
            directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            index = round(wind_direction / 45) % 8
            cardinal = directions[index]

            speed_unit = "m/s" if args.get("units", "metric") == "metric" else "mph"
            return f"Wind in {location}: {wind_speed} {speed_unit} from {cardinal} ({wind_direction}°)"

        # Implement other verbs (sunrise-sunset, uv-index, etc.)
        # ...

        return None  # Let default execution happen for unhandled verbs

    def _fetch_weather_data(self, location, units="metric"):
        """Fetch current weather data from the API."""
        try:
            query = urllib.parse.quote(location)
            url = f"{self.base_url}/weather?q={query}&units={units}&appid={self.api_key}"

            with urllib.request.urlopen(url) as response:
                return json.loads(response.read().decode("utf-8"))

        except urllib.error.HTTPError as e:
            if e.code == 404:
                return f"Location '{location}' not found."
            elif e.code == 401:
                return "Invalid API key. Please check your OpenWeatherMap API key."
            else:
                return f"HTTP error: {e.code} - {e.reason}"

        except Exception as e:
            return f"Error fetching weather data: {str(e)}"

    def _get_current_weather(self, location, units="metric"):
        """Format current weather data for display."""
        weather_data = self._fetch_weather_data(location, units)
        if isinstance(weather_data, str):  # Error message
            return weather_data

        try:
            temp = weather_data.get("main", {}).get("temp")
            feels_like = weather_data.get("main", {}).get("feels_like")
            humidity = weather_data.get("main", {}).get("humidity")
            description = weather_data.get("weather", [{}])[0].get("description", "")
            wind_speed = weather_data.get("wind", {}).get("speed")

            unit_symbol = "°C" if units == "metric" else "°F"
            speed_unit = "m/s" if units == "metric" else "mph"

            return f"""
                Current weather in {location}:
                ----------------------------
                Temperature: {temp}{unit_symbol} (feels like {feels_like}{unit_symbol})
                Condition: {description.capitalize()}
                Humidity: {humidity}%
                Wind Speed: {wind_speed} {speed_unit}
            """

        except Exception as e:
            return f"Error processing weather data: {str(e)}"

    def _get_forecast(self, location, days=5, units="metric"):
        """Get and format weather forecast."""
        try:
            query = urllib.parse.quote(location)
            url = f"{self.base_url}/forecast?q={query}&units={units}&appid={self.api_key}"

            with urllib.request.urlopen(url) as response:
                forecast_data = json.loads(response.read().decode("utf-8"))

            # The API returns forecast in 3-hour intervals
            # We'll simplify by grouping by day and showing min/max temps

            # Process the forecast data...
            # (Implementation details omitted for brevity)

            return "Forecast data processed successfully."  # Placeholder for the actual formatted forecast

        except Exception as e:
            return f"Error fetching forecast data: {str(e)}"

# Register the plugin
registry.register(WeatherAPIPlugin())
```

## Best Practices for Plugin Development

### 1. Error Handling and Graceful Degradation

Always implement robust error handling in your plugins:

```python
def execute_command(self, verb, args, command):
    try:
        # Your implementation here
        return result
    except Exception as e:
        logging.error(f"Error in {self.name} plugin: {str(e)}")
        return f"An error occurred: {str(e)}"
```

For optional dependencies, implement graceful degradation:

```python
try:
    import some_optional_library
    HAS_LIBRARY = True
except ImportError:
    HAS_LIBRARY = False

# Later in your code
if HAS_LIBRARY:
    # Use the library
else:
    # Fall back to simpler implementation
```

### 2. Security Considerations

- Validate all user inputs before using them in commands
- Use parameter binding instead of string interpolation when possible
- Be especially careful with any plugin that:
  - Executes shell commands
  - Makes network requests
  - Accesses the file system
  - Runs with elevated privileges

Example of secure command generation:

```python
# Insecure way (vulnerable to injection)
def generate_command(self, verb, args):
    filename = args.get("filename")
    return f"cat {filename}"  # Dangerous!

# Secure way
def generate_command(self, verb, args):
    filename = args.get("filename", "")
    if not filename or ".." in filename or filename.startswith("/"):
        return "echo 'Invalid filename'"

    # Use shlex.quote to properly escape the filename
    import shlex
    safe_filename = shlex.quote(filename)
    return f"cat {safe_filename}"
```

### 3. Testing Your Plugins

Create a comprehensive test suite for your plugin:

```python
import unittest
from plainspeak.plugins.base import registry
from your_plugin import YourPlugin

class TestYourPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = YourPlugin()

    def test_get_verbs(self):
        verbs = self.plugin.get_verbs()
        self.assertIn("your-verb", verbs)

    def test_generate_command(self):
        command = self.plugin.generate_command(
            "your-verb",
            {"param": "test"}
        )
        self.assertEqual(command, "expected command")

    def test_error_handling(self):
        command = self.plugin.generate_command(
            "your-verb",
            {"param": ""}  # Empty param should be handled gracefully
        )
        self.assertIn("error", command.lower())

if __name__ == "__main__":
    unittest.main()
```

### 4. Documentation

Document your plugin thoroughly:

1. Create a README.md file in your plugin directory
2. Include examples of natural language commands your plugin can handle
3. Document any configuration options or environment variables
4. Explain any dependencies or setup requirements

Example plugin README structure:

```markdown
# YourPlugin

## Description
Brief description of what your plugin does and why it's useful.

## Installation
How to install and configure your plugin.

## Dependencies
List any required or optional dependencies.

## Usage Examples
Examples of natural language commands that work with your plugin:

- "your-verb with parameter"
- "another-verb with multiple parameters"

## Configuration Options
Explanation of any configuration options.

## API Keys and Security
Information about handling API keys or sensitive data.
```

## Publishing Your Plugin

### 1. Package Structure

Organize your plugin as a proper Python package:

```
your-plugin/
├── README.md
├── setup.py
├── your_plugin/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
└── tests/
    ├── __init__.py
    └── test_your_plugin.py
```

Example `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="plainspeak-your-plugin",
    version="1.0.0",
    description="Your plugin description",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "plainspeak>=1.0.0",
        # Other dependencies
    ],
    entry_points={
        "plainspeak.plugins": [
            "your-plugin=your_plugin.main:register_plugin",
        ],
    }
)
```

### 2. Distribution

Publish your plugin to PyPI:

```bash
# Build the package
python setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
```

### 3. Integration with PlainSpeak

Users can then install your plugin with:

```bash
pip install plainspeak-your-plugin
```

PlainSpeak will automatically discover and load your plugin through the entry point.

## Conclusion

In this tutorial, we've covered advanced plugin development techniques including:

- Building context-aware plugins that maintain state
- Creating plugins with rich visual output
- Developing plugins that integrate with external APIs
- Implementing best practices for security and error handling
- Packaging and distributing your plugins

As you develop more sophisticated plugins, remember that the goal is to make complex operations accessible through natural language. Focus on creating intuitive interfaces that align with how users naturally express their intentions, and your plugins will provide tremendous value to the PlainSpeak ecosystem.
