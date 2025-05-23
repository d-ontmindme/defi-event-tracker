import json
import re
from urllib import request
from urllib.error import URLError


def fetch_discourse_latest(base_url):
    """Return JSON from a Discourse forum's /latest.json endpoint."""
    url = base_url.rstrip('/') + '/latest.json'
    try:
        with request.urlopen(url) as resp:
            return json.load(resp)
    except URLError:
        return None


def fetch_reddit_posts(base_url):
    """Return JSON from a subreddit using Reddit's JSON endpoint."""
    match = re.search(r'reddit\.com/(r/[^/]+)', base_url)
    if not match:
        return None
    api = f'https://www.reddit.com/{match.group(1)}/new.json?limit=50'
    req = request.Request(api, headers={'User-Agent': 'proposal-tracker/0.1'})
    try:
        with request.urlopen(req) as resp:
            return json.load(resp)
    except URLError:
        return None


def fetch_github_discussions(base_url):
    """Return JSON for repository discussions via GitHub API."""
    match = re.search(r'github\.com/([^/]+)/([^/]+)', base_url)
    if not match:
        return None
    owner, repo = match.group(1), match.group(2)
    api = f'https://api.github.com/repos/{owner}/{repo}/discussions'
    req = request.Request(api, headers={'Accept': 'application/vnd.github+json'})
    try:
        with request.urlopen(req) as resp:
            return json.load(resp)
    except URLError:
        return None


def fetch_x23_proposals(base_url):
    """Return JSON from the x23.ai governance API."""
    url = base_url.rstrip('/') + '/proposals'
    try:
        with request.urlopen(url) as resp:
            return json.load(resp)
    except URLError:
        return None
