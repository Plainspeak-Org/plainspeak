"""
Calendar Plugin for PlainSpeak.

This module provides calendar operations through natural language.
"""

import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import icalendar  # type: ignore[import-untyped]
import pytz  # type: ignore[import-untyped]
from dateutil.parser import parse as parse_date  # type: ignore[import-untyped]
from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]

from .base import YAMLPlugin, registry
from .platform import platform_manager


class CalendarStore:
    """Storage for calendar data using iCalendar format."""

    def __init__(self, calendar_dir: Optional[Path] = None):
        """
        Initialize calendar storage.

        Args:
            calendar_dir: Directory for calendar files. If None, uses ~/.plainspeak/calendar
        """
        if calendar_dir is None:
            calendar_dir = Path.home() / ".plainspeak" / "calendar"

        self.calendar_dir = calendar_dir
        self.calendar_dir.mkdir(parents=True, exist_ok=True)
        self.calendar_file = self.calendar_dir / "events.ics"

        # Initialize or load calendar
        if not self.calendar_file.exists():
            self.calendar = icalendar.Calendar()
            self.calendar.add("prodid", "-//PlainSpeak Calendar//EN")
            self.calendar.add("version", "2.0")
            self._save_calendar()
        else:
            self._load_calendar()

    def _load_calendar(self) -> None:
        """Load calendar from file."""
        with open(self.calendar_file, "rb") as f:
            calendar_bytes = f.read()
            # Convert bytes to string for from_ical
            calendar_str = calendar_bytes.decode("utf-8", errors="replace")
            # Create new calendar instance
            self.calendar = icalendar.Calendar()

            # Parse the existing calendar data
            imported_cal = icalendar.Calendar.from_ical(calendar_str)

            # Copy properties and components
            for attr, value in imported_cal.items():
                self.calendar[attr] = value

            for component in imported_cal.subcomponents:
                self.calendar.add_component(component)

    def _save_calendar(self) -> None:
        """Save calendar to file."""
        with open(self.calendar_file, "wb") as f:
            f.write(self.calendar.to_ical())

    def add_event(
        self,
        title: str,
        start: Union[str, datetime],
        end: Optional[Union[str, datetime]] = None,
        location: str = "",
        description: str = "",
    ) -> str:
        """
        Add a calendar event.

        Args:
            title: Event title
            start: Start time
            end: Optional end time
            location: Optional location
            description: Optional description

        Returns:
            Event ID (UUID)
        """
        # Parse dates if needed
        if isinstance(start, str):
            start = parse_date(start)
        if end and isinstance(end, str):
            end = parse_date(end)
        elif not end:
            # Default to 1 hour duration
            end = start + timedelta(hours=1)

        # Create event
        event = icalendar.Event()
        event_id = str(uuid.uuid4())
        event.add("uid", event_id)
        event.add("summary", title)
        event.add("dtstart", start)
        event.add("dtend", end)

        if location:
            event.add("location", location)
        if description:
            event.add("description", description)

        # Add to calendar and save
        self.calendar.add_component(event)
        self._save_calendar()

        return event_id

    def edit_event(
        self,
        event_id: str,
        title: Optional[str] = None,
        start: Optional[Union[str, datetime]] = None,
        end: Optional[Union[str, datetime]] = None,
        location: Optional[str] = None,
    ) -> bool:
        """
        Edit a calendar event.

        Args:
            event_id: Event UUID
            title: Optional new title
            start: Optional new start time
            end: Optional new end time
            location: Optional new location

        Returns:
            True if event was found and edited
        """
        for component in self.calendar.walk("VEVENT"):
            if str(component.get("uid")) == event_id:
                if title:
                    component["summary"] = title
                if start:
                    if isinstance(start, str):
                        start = parse_date(start)
                    component["dtstart"] = start
                if end:
                    if isinstance(end, str):
                        end = parse_date(end)
                    component["dtend"] = end
                if location is not None:  # Allow empty string to clear location
                    component["location"] = location

                self._save_calendar()
                return True

        return False

    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event.

        Args:
            event_id: Event UUID

        Returns:
            True if event was found and deleted
        """
        for component in self.calendar.walk("VEVENT"):
            if str(component.get("uid")) == event_id:
                self.calendar.subcomponents.remove(component)
                self._save_calendar()
                return True
        return False

    def list_events(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List calendar events.

        Args:
            start: Optional start time filter
            end: Optional end time filter
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        events = []
        for component in self.calendar.walk("VEVENT"):
            event_start = component.get("dtstart").dt
            event_end = component.get("dtend").dt

            # Apply time filters if specified
            if start and event_end < start:
                continue
            if end and event_start > end:
                continue

            events.append(
                {
                    "id": str(component.get("uid")),
                    "title": str(component.get("summary")),
                    "start": event_start,
                    "end": event_end,
                    "location": str(component.get("location", "")),
                    "description": str(component.get("description", "")),
                }
            )

            if len(events) >= limit:
                break

        return sorted(events, key=lambda e: e["start"])

    def search_events(
        self,
        query: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for events.

        Args:
            query: Search text
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of matching events
        """
        query = query.lower()
        matching_events = []

        for component in self.calendar.walk("VEVENT"):
            # Check if event matches query
            summary = str(component.get("summary", "")).lower()
            location = str(component.get("location", "")).lower()
            description = str(component.get("description", "")).lower()

            if not (query in summary or query in location or query in description):
                continue

            # Apply date filters
            event_start = component.get("dtstart").dt
            event_end = component.get("dtend").dt

            if start_date and event_end < start_date:
                continue
            if end_date and event_start > end_date:
                continue

            matching_events.append(
                {
                    "id": str(component.get("uid")),
                    "title": str(component.get("summary")),
                    "start": event_start,
                    "end": event_end,
                    "location": str(component.get("location", "")),
                    "description": str(component.get("description", "")),
                }
            )

        return sorted(matching_events, key=lambda e: e["start"])

    def import_calendar(self, file_path: Union[str, Path]) -> int:
        """
        Import events from an iCalendar file.

        Args:
            file_path: Path to .ics file

        Returns:
            Number of events imported

        Raises:
            ValueError: If file format is invalid
        """
        file_path = Path(file_path)
        if not file_path.exists() or file_path.suffix != ".ics":
            raise ValueError("Invalid calendar file")

        try:
            with open(file_path, "rb") as f:
                imported_bytes = f.read()
                # Convert bytes to string for from_ical
                imported_str = imported_bytes.decode("utf-8", errors="replace")
                imported_cal = icalendar.Calendar.from_ical(imported_str)

            count = 0
            for component in imported_cal.walk("VEVENT"):
                # Add each event to our calendar
                self.calendar.add_component(component)
                count += 1

            self._save_calendar()
            return count

        except Exception as e:
            raise ValueError(f"Failed to import calendar: {str(e)}")

    def _format_event_time(self, start: Union[str, datetime], end: Optional[Union[str, datetime]] = None) -> str:
        """Format event time for display."""
        if isinstance(start, str):
            start = parse_date(start)

        if end is None:
            return start.strftime("%Y-%m-%d %H:%M")

        if isinstance(end, str):
            end = parse_date(end)

        # Now both start and end are datetime objects
        if start.date() == end.date():
            return f"{start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%H:%M')}"
        else:
            return f"{start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%Y-%m-%d %H:%M')}"


class CalendarPlugin(YAMLPlugin):
    """
    Plugin for calendar operations.

    Features:
    - Event management (add, edit, delete)
    - Calendar views (day, week, month)
    - Event search and filtering
    - iCalendar import/export
    """

    def __init__(self):
        """Initialize the calendar plugin."""
        yaml_path = Path(__file__).parent / "calendar.yaml"
        super().__init__(yaml_path)

        self.store = CalendarStore()
        self.local_tz = pytz.timezone("UTC")  # Default to UTC

    def _preprocess_args(self, verb: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess command arguments.

        Args:
            verb: The verb being used.
            args: Original arguments.

        Returns:
            Processed arguments.
        """
        processed = args.copy()

        # Handle date/time values
        for field in ["start", "end", "date", "start_date", "end_date"]:
            if field in processed and processed[field]:
                try:
                    # Parse relative dates (e.g., "tomorrow", "next week")
                    value = processed[field].lower()
                    if value == "today":
                        dt = datetime.now()
                    elif value == "tomorrow":
                        dt = datetime.now() + timedelta(days=1)
                    elif value == "next week":
                        dt = datetime.now() + timedelta(weeks=1)
                    elif value == "next month":
                        dt = datetime.now() + relativedelta(months=1)
                    else:
                        dt = parse_date(value)

                    processed[field] = dt.isoformat()
                except (ValueError, TypeError):
                    pass

        # Handle file paths
        if "file" in processed:
            path = processed["file"]
            if path:
                processed["file"] = platform_manager.convert_path_for_command(path)

        return processed

    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """
        Generate a calendar command.

        Args:
            verb: The verb to handle.
            args: Arguments for the verb.

        Returns:
            The generated command string.
        """
        # Preprocess arguments
        args = self._preprocess_args(verb, args)

        # Apply defaults for common cases
        if verb == "list-events" and not any([args.get(x) for x in ["start", "end", "today", "week", "month"]]):
            args["today"] = True  # Default to today's events

        if verb == "show-calendar" and "view" not in args:
            args["view"] = "month"  # Default to month view

        # Generate command using parent's implementation
        return super().generate_command(verb, args)


# Create and register the plugin instance
try:
    calendar_plugin = CalendarPlugin()
    registry.register(calendar_plugin)
except Exception as e:
    # Log error but don't prevent other plugins from loading
    import logging

    logger = logging.getLogger(__name__)
    logger.warning("Failed to load Calendar plugin: %s", str(e))
