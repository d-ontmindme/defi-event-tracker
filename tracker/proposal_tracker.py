"""Utilities for collecting governance proposals from various forums."""

import json
import re
from typing import Dict, List

from . import config
from .forum_clients import (
    fetch_discourse_latest,
    fetch_reddit_posts,
    fetch_github_discussions,
)


class ProposalTracker:
    """Collect proposals from a set of governance forums."""

    def __init__(self, forums: Dict[str, str]):
        """Initialize with a mapping of forum names to base URLs."""
        self.forums = forums
        self.state: Dict[str, List[Dict]] = {}

    def fetch_forum_proposals(self, forum_name: str, base_url: str) -> List[Dict]:
        """Fetch proposals for a single forum based on the URL."""
        if not base_url:
            return []

        # Reddit
        if 'reddit.com' in base_url:
            data = fetch_reddit_posts(base_url)
            if not data:
                return []
            proposals = []
            for post in data.get('data', {}).get('children', []):
                pdata = post.get('data', {})
                title = pdata.get('title', '')
                if re.search(r'proposal', title, re.IGNORECASE):
                    proposals.append({
                        'id': pdata.get('id'),
                        'title': title,
                        'created_at': pdata.get('created_utc'),
                        'url': 'https://www.reddit.com' + pdata.get('permalink', ''),
                    })
            return proposals

        # GitHub Discussions
        if 'github.com' in base_url:
            data = fetch_github_discussions(base_url)
            if not data:
                return []
            proposals = []
            for disc in data:
                title = disc.get('title', '')
                if re.search(r'proposal', title, re.IGNORECASE):
                    proposals.append({
                        'id': disc.get('number'),
                        'title': title,
                        'created_at': disc.get('created_at'),
                        'url': disc.get('html_url'),
                    })
            return proposals

        # Default to Discourse
        data = fetch_discourse_latest(base_url)
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
