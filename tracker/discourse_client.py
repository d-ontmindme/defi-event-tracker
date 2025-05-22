import json
from urllib import request
from urllib.error import URLError


def fetch_latest_topics(base_url):
    """Fetch latest topics JSON from a discourse forum.

    Returns the parsed JSON object or None if the request fails.
    """
    url = base_url.rstrip('/') + '/latest.json'
    try:
        with request.urlopen(url) as resp:
            return json.load(resp)
    except URLError:
        return None
