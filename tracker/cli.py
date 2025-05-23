import argparse
import json

from . import config
from .proposal_tracker import ProposalTracker


def load_forums(path: str) -> dict:
    """Load forums mapping from a JSON file."""
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Config file must contain an object mapping names to URLs")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch governance proposals from forums")
    parser.add_argument(
        "-c", "--config",
        help="Path to JSON file mapping forum names to URLs (defaults to tracker.config)",
    )
    parser.add_argument(
        "-o", "--output", default="proposals.json", help="File to write proposal data to"
    )
    parser.add_argument(
        "-f", "--forums", nargs="+", help="Limit to specific forum names"
    )
    args = parser.parse_args(argv)

    forums = (
        load_forums(args.config)
        if args.config
        else {k: v for k, v in config.FORUMS.items() if v}
    )

    if args.forums:
        forums = {name: forums[name] for name in args.forums if name in forums}

    tracker = ProposalTracker(forums)
    tracker.update()
    tracker.save_state(args.output)
    print(f"Saved proposals to {args.output}")


if __name__ == "__main__":
    main()
