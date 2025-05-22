import json
import re
from typing import Dict, List

from . import config
from .discourse_client import fetch_latest_topics


class ProposalTracker:
    def __init__(self, forums: Dict[str, str]):
        self.forums = forums
        self.state: Dict[str, List[Dict]] = {}

    def fetch_forum_proposals(self, forum_name: str, base_url: str):
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
        for name, url in self.forums.items():
            self.state[name] = self.fetch_forum_proposals(name, url)

    def save_state(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.state, f, indent=2)

    def load_state(self, path: str):
        with open(path) as f:
            self.state = json.load(f)


def main():
    tracker = ProposalTracker(config.FORUMS)
    tracker.update()
    tracker.save_state('proposals.json')
    print(json.dumps(tracker.state, indent=2))


if __name__ == '__main__':
    main()
