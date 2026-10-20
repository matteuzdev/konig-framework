"""Explicit-host CLI."""
import argparse
import json
from .core import extract

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--allow-host", action="append", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(extract(args.url, allowed_hosts=tuple(args.allow_host)).json(), ensure_ascii=False))
    except Exception as exc:
        parser.exit(1, f"Extraction failed: {type(exc).__name__}\n")

if __name__ == "__main__":
    main()
