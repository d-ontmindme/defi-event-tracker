# DeFi Governance Proposal Tracker

This repository contains a simple Python program that collects governance
proposals from Discourse-based forums used by various crypto projects.

## Usage

1. Ensure Python 3 is available.
2. Run `python3 -m tracker.proposal_tracker` to fetch proposals and store them
   in `proposals.json`.
3. Customize the forums tracked by editing `tracker/config.py`.

## Testing

Run the unit tests with:

```
python3 -m unittest discover -s tests
```
