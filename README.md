# DeFi Governance Forum Tracker

This repository contains a script to pair crypto assets listed on Messari with their corresponding governance forums on Snapshot.

## Requirements

- Python 3.8+
- `requests` library (`pip install requests`)

## Usage

Run the following command to fetch assets and their governance forums:

```bash
python scripts/fetch_governance_forums.py
```

The script queries Messari's assets API and Snapshot's spaces API. It attempts to match assets by their symbol. The matched list is written to `governance_forums.json` in the repository root.

**Note:** This environment doesn't provide network access by default, so executing the script here won't succeed. Run the script in an environment with internet connectivity.
