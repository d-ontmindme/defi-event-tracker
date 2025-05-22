"""Utilities for collecting governance proposals from various forums."""

import json
import re
from typing import Dict, List

from . import config
from .discourse_client import fetch_latest_topics


class ProposalTracker:
    """Collect proposals from a set of governance forums."""

    def __init__(self, forums: Dict[str, str]):
        """Initialize with a mapping of forum names to base URLs."""
        self.forums = forums
        self.state: Dict[str, List[Dict]] = {}

    def fetch_forum_proposals(self, forum_name: str, base_url: str):
        """Return a list of proposal dictionaries for the given forum."""
        data = fetch_latest_topics(base_url)
        proposals = []
        if not data or 'topic_list' not in data:
            return proposals
        for topic in data['topic_list'].get('topics', []):
            title = topic.get('title', '')
            if re.search(r'proposal', title, re.IGNORECASE):
                proposals.append({
                    'id': topic.get('id'),
                    'title': title,
                    'created_at': topic.get('created_at'),
                    'url': f"{base_url}/t/{topic.get('slug')}" if topic.get('slug') else None,
                })
        return proposals

    def update(self):
        """Fetch proposals from all configured forums and update state."""
        for name, url in self.forums.items():
            self.state[name] = self.fetch_forum_proposals(name, url)

    def save_state(self, path: str):
        """Write the current state to ``path`` in JSON format."""
        with open(path, 'w') as f:
            json.dump(self.state, f, indent=2)

    def load_state(self, path: str):
        """Load proposal data from ``path`` into ``state``."""
        with open(path) as f:
            self.state = json.load(f)


def main():
    """Simple command-line entry point for running the tracker."""
    tracker = ProposalTracker(config.FORUMS)
    tracker.update()
    tracker.save_state('proposals.json')
    print(json.dumps(tracker.state, indent=2))


if __name__ == '__main__':
    main()
