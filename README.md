# DeFi Governance Proposal Tracker

This repository contains an experimental tool for gathering governance
proposals from communities in the decentralized finance (DeFi) space. It
pulls topics from Discourse-based forums and stores any post that has the
word "proposal" in its title. The resulting data can be used as a starting
point for tracking governance activity across many projects.

## Overview

The codebase is intentionally simple:

- **`tracker/proposal_tracker.py`** – orchestrates fetching topics from each
  configured forum and writing the results to `proposals.json`.
- **`tracker/discourse_client.py`** – provides a small helper for retrieving
  the `/latest.json` feed from a Discourse forum.
- **`tracker/config.py`** – maps project names to the base URL of their
  governance forum. Values may be `None` when no forum has been located.
- **`scripts/fetch_governance_forums.py`** – optional script that pairs asset
  data from Messari with Snapshot voting spaces to produce
  `governance_forums.json`.

The project currently focuses on gathering raw proposal links. Further
features such as historical analysis or metrics can be built on top of this
foundation.

## Requirements

- Python 3.7 or later.
- Internet access when running the tracker so it can reach the specified
  forums. (The test suite does not require network access.)

## Running the tracker

1. Edit `tracker/config.py` to choose which forums you wish to poll. The file
   already includes many examples. Only entries with a valid URL will be
   queried.
2. Execute the module directly:

   ```bash
   python3 -m tracker.proposal_tracker
   ```

   After running, a `proposals.json` file will be created in the project root
   containing the proposals fetched from each forum. The data structure is a
   dictionary keyed by forum name.

### Customizing

You can adapt the tracker to other platforms by modifying the
`fetch_forum_proposals` method in `tracker/proposal_tracker.py`. At present it
searches for the word "proposal" in topic titles. Adjust this logic as needed
for different communities or additional filtering.

The helper script in `scripts/` demonstrates how you might discover governance
forums automatically using the Messari and Snapshot APIs. Running that script
requires external network access.

## Testing

Unit tests are located in the `tests` directory and rely on the example data in
`sample_data/`. Execute them with:

```bash
python3 -m unittest discover -s tests
```

Running the tests ensures that basic proposal extraction logic works as
expected without hitting real forums.

