
"""Utilities for collecting governance proposals from various forums.

This module has been extended to optionally analyse each discovered proposal
with the OpenAI API.  The analysis provides an ``importance`` label
(``Low``/``Mid``/``High``) and a two line summary of the proposal.  When the
OpenAI package is not available or an API key is not configured the tracker will
fall back to a simple heuristic implementation so unit tests can run without
network access.
"""

import json
import os
from typing import Callable, Dict, List

from . import config
from .forum_clients import (
    fetch_discourse_latest,
    fetch_reddit_posts,
    fetch_github_discussions,
    fetch_x23_proposals,
)


class ProposalTracker:
    """Collect proposals from a set of governance forums."""

    def __init__(self, forums: Dict[str, str], analyzer: Callable[[str], Dict[str, str]] | None = None):
        """Initialize with a mapping of forum names to base URLs.

        ``analyzer`` is a callable that accepts proposal text and returns a
        mapping with ``importance`` and ``summary`` keys.  When omitted a default
        implementation backed by the OpenAI API (with a local fallback) is used.
        """
        self.forums = forums
        self.analyzer = analyzer or self._default_analyzer
        self.state: Dict[str, List[Dict]] = {}

    def _default_analyzer(self, text: str) -> Dict[str, str]:
        """Analyse ``text`` and return importance and summary.

        When the ``openai`` package or an API key is not available a very simple
        heuristic is used so that tests remain deterministic without network
        access.
        """
        try:
            import openai  # type: ignore

            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                prompt = (
                    "Classify the importance of the following proposal as Low, "
                    "Mid or High and provide a two line summary.\n" + text
                )
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                )
                content = resp["choices"][0]["message"]["content"]
                lines = [l.strip() for l in content.splitlines() if l.strip()]
                if lines:
                    importance = lines[0].split()[0].capitalize()
                    summary = "\n".join(lines[1:3]) if len(lines) > 1 else ""
                    return {"importance": importance, "summary": summary}
        except Exception:
            pass

        # Fallback simple analyser
        importance = "High" if "!" in text or len(text) > 80 else "Low"
        summary = text.strip()[:100]
        return {"importance": importance, "summary": summary}

    def fetch_forum_proposals(self, forum_name: str, base_url: str) -> List[Dict]:
        """Fetch proposals for a single forum based on the URL."""
        if not base_url:
            return []

        # x23.ai governance API
        if 'api.x23.ai' in base_url:
            data = fetch_x23_proposals(base_url)
            if not data:
                return []
            proposals = []
            for prop in data.get('proposals', []):
                title = prop.get('title', '')
                analysis = self.analyzer(title)
                proposals.append({
                    'id': prop.get('id'),
                    'title': title,
                    'created_at': prop.get('created_at'),
                    'url': prop.get('url'),
                    'importance': analysis['importance'],
                    'summary': analysis['summary'],
                })
            return proposals

        # Reddit
        if 'reddit.com' in base_url:
            data = fetch_reddit_posts(base_url)
            if not data:
                return []
            proposals = []
            for post in data.get('data', {}).get('children', []):
                pdata = post.get('data', {})
                title = pdata.get('title', '')
                analysis = self.analyzer(title)
                proposals.append({
                    'id': pdata.get('id'),
                    'title': title,
                    'created_at': pdata.get('created_utc'),
                    'url': 'https://www.reddit.com' + pdata.get('permalink', ''),
                    'importance': analysis['importance'],
                    'summary': analysis['summary'],
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
                analysis = self.analyzer(title)
                proposals.append({
                    'id': disc.get('number'),
                    'title': title,
                    'created_at': disc.get('created_at'),
                    'url': disc.get('html_url'),
                    'importance': analysis['importance'],
                    'summary': analysis['summary'],
                })
            return proposals

        # Default to Discourse
        data = fetch_discourse_latest(base_url)
        proposals = []
        if not data or 'topic_list' not in data:
            return proposals

        for topic in data['topic_list'].get('topics', []):
            title = topic.get('title', '')
            analysis = self.analyzer(title)
            proposals.append({
                'id': topic.get('id'),
                'title': title,
                'created_at': topic.get('created_at'),
                'url': f"{base_url}/t/{topic.get('slug')}" if topic.get('slug') else None,
                'importance': analysis['importance'],
                'summary': analysis['summary'],
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
