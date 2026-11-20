"""Download the Higgsfield originals listed in sources.json into raw/ (raw/ is not committed).

The raw files were lost with the local folder on 16-19 Nov 2026. sources.json was rebuilt on 20 Nov 2026 by
matching the account's generation history to jobs.json (checked against the iris / eye coordinates in
process.py and ba.py). After fetching, run process.py to rebuild the site's .webp files.

Usage: python fetch_raw.py [name ...]
"""
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"


def main():
    RAW.mkdir(exist_ok=True)
    src = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    for name, s in src.items():
        if sys.argv[1:] and name not in sys.argv[1:]:
            continue
        out = RAW / f"{name}.png"
        if out.exists():
            continue
        urllib.request.urlretrieve(s["url"], out)
        print(name)


if __name__ == "__main__":
    main()
