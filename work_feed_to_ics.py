#!/usr/bin/env python3
import os
import requests
from datetime import datetime, timezone
from ics import Calendar, Event

# === CONFIG ===
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
DATABASE_ID  = os.environ.get("NOTION_DB_ID", "29520c51aebe80798d10db123c986db0")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN environment variable not set. Check your .env file.")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# === FUNCTIONS ===

def query_database(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    results = []
    payload = {}
    while True:
        resp = requests.post(url, headers=HEADERS, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"Notion API error {resp.status_code}: {resp.text}")
        data = resp.json()
        results.extend(data["results"])
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return results

def create_ics(events):
    cal = Calendar()
    for event in events:
        try:
            title = event["properties"][" Calendar"]["title"][0]["plain_text"]
            start = event["properties"]["Time"]["date"]["start"]
            end = event["properties"]["Time"]["date"].get("end", start)
            steps_list = event["properties"].get("Actionable Steps", {}).get("rich_text", [])
            description = steps_list[0]["plain_text"] if steps_list else ""
        except (KeyError, IndexError, TypeError):
            continue
        e = Event()
        e.name = title
        e.begin = start
        e.end = end
        e.description = description
        cal.events.add(e)
    with open("Work Feed.ics", "w") as f:
        f.writelines(cal)
    print(f"  Wrote Work Feed.ics ({len(cal.events)} events)")

def main():
    print("Querying Work database...")
    events = query_database(DATABASE_ID)
    print(f"  {len(events)} entries found")
    create_ics(events)
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"Feed updated at {now}")

if __name__ == "__main__":
    main()
