    #!/usr/bin/env python3
"""
Download the full Messari asset list (name + symbol).

• Requires: requests     (pip install requests)
• Optional: pandas       (only if you want the DataFrame preview)
• Set env var MESSARI_API_KEY or edit API_KEY below.
"""

from __future__ import annotations
import os
import time
from typing import Dict, List, Union
import requests
import pandas as pd           # ← comment out if you don’t need Pandas

BASE_URL  = "https://api.messari.io/metrics/v1/assets"
PER_PAGE  = 500               # API max as of 2025-05
API_KEY   = "G-EDma0tYGvItk6jNavKl9dQ-EXj67lxODic2KObO8lWEx7w"  # set it or leave empty for public access
RATE_WAIT = 0.15              # ~60 req/min for free tier


def fetch_all_assets(per_page: int = PER_PAGE) -> List[Dict]:
    """
    Return a list of dicts with keys 'name' and 'symbol' for every asset Messari lists.
    Handles both page-based and cursor-based pagination automatically.
    """
    headers = {"Accept": "application/json"}
    if API_KEY and API_KEY != "xxx":
        headers["x-messari-api-key"] = API_KEY

    params: Dict[str, Union[str, int]] = {
        "limit": per_page,
        # ask Messari to return only the fields we need
        "fields": "name,symbol",
    }

    page_or_cursor: Union[int, str] = 1    # can be an int (page) or str (cursor)
    more = True
    out: List[Dict] = []

    while more:
        if isinstance(page_or_cursor, int):
            params["page"] = page_or_cursor
            params.pop("cursor", None)
        else:
            params["cursor"] = page_or_cursor
            params.pop("page", None)

        resp = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()

        # rows live either in data.rows (Metrics endpoint) or data (legacy tiers)
        rows = (
            payload.get("data", {}).get("rows")
            or payload.get("data", [])
        )
        if not rows:                      # nothing left
            break

        # keep only name + symbol
        out.extend(
            {"name": r.get("name"), "symbol": r.get("symbol")}
            for r in rows
            if isinstance(r, dict)
        )

        # --- work out what "the next page" is -------------------------------
        meta = payload.get("meta", {})
        next_cursor = meta.get("cursors", {}).get("next")
        if next_cursor:
            page_or_cursor = next_cursor
            more = True
        else:
            total_pages = meta.get("pagination", {}).get("total_pages")
            # if meta gives us a page count, use it; otherwise guess from rows
            if total_pages:
                more = page_or_cursor < total_pages
            else:
                more = len(rows) == per_page
            if more:
                page_or_cursor = (page_or_cursor + 1) if isinstance(page_or_cursor, int) else 2

        if more:
            time.sleep(RATE_WAIT)         # respect public-tier limits

    return out


if __name__ == "__main__":
    assets = fetch_all_assets()
    print(f"Fetched {len(assets):,} assets")

    # Optional quick peek in a DataFrame
    if "pd" in globals():
        df = pd.DataFrame(assets)
        print(df.head())
