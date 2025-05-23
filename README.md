# DeFi Governance Proposal Tracker

This project provides a small utility for gathering governance proposal links from a variety of DeFi community forums.  It polls a list of forums and writes any topics with the word `proposal` in their title to a JSON file.  The resulting data can be used as a starting point for further analysis or monitoring.

## Repository layout

- **`tracker/proposal_tracker.py`** – core logic for fetching topics from each configured forum.
- **`tracker/cli.py`** – command line interface used when running the tool.
- **`tracker/config.py`** – mapping of many popular projects to the URL of their forum (values may be `None` when no forum exists).
- **`tracker/forum_clients.py`** – helper functions for querying Discourse, Reddit, GitHub and x23.ai.
- **`scripts/fetch_governance_forums.py`** – optional helper that pairs Messari asset data with Snapshot spaces (requires network access and the `requests` package).
- **`tests/`** – unit tests using sample forum data from `sample_data/`.

The tracker itself relies only on the Python standard library.  Optional helper scripts may require additional packages such as `requests` or `pandas`.

## Requirements

- Python 3.7 or newer
- Network connectivity when running the tracker so it can query the forums

## Quick start

1. **Select forums** – edit `tracker/config.py` and ensure the `FORUMS` dictionary contains the communities you wish to poll.  Only entries with a valid URL will be queried.
2. **Run the tracker** using the command line interface:

   ```bash
   python3 -m tracker
   ```

   By default this writes a file called `proposals.json` in the repository root.  Each key in the JSON object corresponds to a forum name and maps to a list of proposals discovered for that forum.

### Command line options

```
usage: python -m tracker [-h] [-c CONFIG] [-o OUTPUT] [-f FORUMS [FORUMS ...]]
```

- `--config / -c` – path to a JSON file containing a `{ "name": "url" }` mapping.  When omitted, the built‑in mapping in `tracker.config` is used.
- `--output / -o` – location of the JSON file to write (default: `proposals.json`).
- `--forums / -f` – one or more forum names to poll.  If omitted, all forums from the configuration are used.

Example fetching only the Aave and Uniswap forums and writing to a custom file:

```bash
python3 -m tracker -f Aave Uniswap -o my_proposals.json
```

## Customising behaviour

The simplest way to adapt the tracker is to modify `fetch_forum_proposals` in `tracker/proposal_tracker.py`.  The default implementation looks for the substring `proposal` in the topic title and supports Discourse, Reddit, GitHub Discussions and the `api.x23.ai` governance feed.  Additional platform handlers can be added in `tracker/forum_clients.py`.

The optional `scripts/fetch_governance_forums.py` script demonstrates how to build a mapping of token symbols to Snapshot spaces using the Messari and Snapshot APIs.  Running it requires the `requests` package and internet access:

```bash
python3 scripts/fetch_governance_forums.py
```

## Running tests

Execute the unit tests from the repository root:

```bash
python3 -m unittest discover -s tests
```

The tests use the static files under `sample_data/` and therefore do not require network access.
