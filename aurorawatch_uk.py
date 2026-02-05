#!/usr/bin/env python3
"""
AuroraWatch UK → Home Assistant command_line sensor helper.

Fetches AuroraWatch UK's alerting-site activity feed (XML), extracts the most recent
<activity> sample, and prints a single line of JSON for Home Assistant to ingest as a 
command_line sensor.
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# ---------------- CONFIG ----------------

CONTACT_EMAIL = "user@example.com"   # <-- change this

URL = "https://aurorawatch-api.lancs.ac.uk/0.2.5/status/alerting-site-activity.xml"

HDR = {
    "User-Agent": f"Home Assistant AuroraWatchUK ({CONTACT_EMAIL})",
    "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
}

# --------------------------------------

# Helper: ISO8601 timestamp in UTC with trailing 'Z'
now = lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# Default payload (safe fallback)
out = {
    "state": "unknown",          # float when available, else "unknown"
    "status": "unknown",         # green/yellow/amber/red
    "data_datetime": None,       # datetime of latest activity sample
    "updated": None,             # feed updated timestamp
    "alerting_site": None,       # site code, e.g. "SUM"
    "polled_at": now(),          # when this script ran (UTC)
    "url": "https://aurorawatch.lancs.ac.uk",
    # "icon" is added once status is known
}

try:
    # Fetch XML
    req = urllib.request.Request(URL, headers=HDR)
    xml = urllib.request.urlopen(req, timeout=20).read()

    # Parse XML
    root = ET.fromstring(xml)  # <site_activity ...>

    # Extract site code from site_id (e.g. "site:AWN:SUM" → "SUM")
    sid = root.attrib.get("site_id", "")
    out["alerting_site"] = sid.split(":")[-1] if sid else None

    # Feed-level updated timestamp
    upd = root.findtext("updated/datetime")
    out["updated"] = upd.strip() if upd else None

    # Activity samples (chronological)
    acts = root.findall("activity")
    if acts:
        last = acts[-1]

        status = (last.attrib.get("status_id") or "unknown").strip().lower()
        out["status"] = status
        out["icon"] = "mdi:flare" if status in ("amber", "red") else "mdi:weather-sunny"

        dt = last.findtext("datetime")
        out["data_datetime"] = dt.strip() if dt else None

        val = last.findtext("value")
        out["state"] = float(val) if val else "unknown"

except Exception:
    # Any failure emit default payload
    pass

# Emit JSON for Home Assistant
print(json.dumps(out))
