"""
Google Calendar integration for pushing diff step dates as events.

Setup (one-time):
1. Go to https://console.cloud.google.com and create a project.
2. Enable the Google Calendar API.
3. Create OAuth 2.0 credentials (Desktop app type) and download as
   credentials.json into this project's root directory.
4. Install dependencies:
       pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

On first run, a browser window will open asking you to authorise the app.
The resulting token is cached in token.json so subsequent runs are silent.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
_CREDS_FILE = Path(__file__).parent.parent.parent / "credentials.json"
_TOKEN_FILE  = Path(__file__).parent.parent.parent / "token.json"


def _get_service():
    """Return an authorised Google Calendar service object."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if _TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(_CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        _TOKEN_FILE.write_text(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def push_experiment_to_calendar(
    diff: dict,
    calendar_id: str = "primary",
) -> list[str]:
    """
    Create a Google Calendar event for each step in the experiment.

    Parameters
    ----------
    diff        : the diff dict from load_experiments()
                  (needs "name", "schedule", keys)
    calendar_id : which calendar to write to ("primary" = user's default)

    Returns
    -------
    List of created event IDs.
    """
    service = _get_service()
    event_ids: list[str] = []

    for entry in diff["schedule"]:
        event = {
            "summary": f"[{diff['name']}] {entry.step.name}",
            "description": entry.step.description or "",
            "start": {"date": entry.date.isoformat()},
            "end":   {"date": (entry.date + timedelta(days=1)).isoformat()},
        }
        result = service.events().insert(calendarId=calendar_id, body=event).execute()
        event_ids.append(result["id"])

    return event_ids


def delete_experiment_events(event_ids: list[str], calendar_id: str = "primary") -> None:
    """Delete previously pushed events by their IDs."""
    service = _get_service()
    for eid in event_ids:
        try:
            service.events().delete(calendarId=calendar_id, eventId=eid).execute()
        except Exception:
            pass
