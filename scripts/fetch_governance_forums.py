import json
import requests

MESSARI_ASSETS_URL = "https://data.messari.io/api/v2/assets"
SNAPSHOT_SPACES_URL = "https://hub.snapshot.org/api/spaces"


def fetch_assets(limit=50):
    params = {"limit": limit}
    response = requests.get(MESSARI_ASSETS_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("data", [])


def fetch_snapshot_spaces():
    response = requests.get(SNAPSHOT_SPACES_URL)
    response.raise_for_status()
    data = response.json()
    return data.get("spaces", []) if isinstance(data, dict) else data


def pair_assets_with_spaces(assets, spaces):
    paired = []
    space_by_symbol = {}
    for space in spaces:
        symbol = space.get("symbol")
        if symbol:
            space_by_symbol[symbol.upper()] = space
    for asset in assets:
        symbol = asset.get("symbol", "").upper()
        space = space_by_symbol.get(symbol)
        if space:
            paired.append({
                "symbol": symbol,
                "name": asset.get("name"),
                "messari_slug": asset.get("slug"),
                "snapshot_space": space.get("id"),
                "snapshot_url": f"https://snapshot.org/#/{space.get('id')}"
            })
    return paired


def main():
    assets = fetch_assets()
    spaces = fetch_snapshot_spaces()
    paired = pair_assets_with_spaces(assets, spaces)
    with open("governance_forums.json", "w") as f:
        json.dump(paired, f, indent=2)
    print(f"Saved {len(paired)} paired governance forums to governance_forums.json")


if __name__ == "__main__":
    main()
