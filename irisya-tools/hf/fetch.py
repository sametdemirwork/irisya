"""Download the Higgsfield generations the site uses into raw/<name>.png (see sources.json).

sources.json maps each raw name to the Higgsfield generation it came from (id, creation time, CDN file name).
It was rebuilt on 2026-11-20 from the account's generation history after the project folder was lost:
every pick was checked by eye, and the portraits against the eye coordinates in process.py and ba.py.

The CDN folder of the account is not stored in the repository. Copy it from any result URL in
Higgsfield (the part before /hf_...) into the HF_CDN environment variable:

  set HF_CDN=https://<cdn-host>/<user-folder>      (PowerShell: $env:HF_CDN = "...")
  python fetch.py               # every missing raw
  python fetch.py --force       # download again
"""
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"


def main():
    cdn = os.environ.get("HF_CDN", "").rstrip("/")
    if not cdn:
        sys.exit("Set HF_CDN to the Higgsfield CDN folder first (see the docstring).")
    force = "--force" in sys.argv
    RAW.mkdir(exist_ok=True)
    src = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))

    def get(item):
        name, e = item
        out = RAW / f"{name}.png"
        if out.exists() and not force:
            return name, "skip"
        urllib.request.urlretrieve(f"{cdn}/{e['file']}", out)
        return name, "ok"

    with ThreadPoolExecutor(8) as ex:
        for name, st in ex.map(get, src.items()):
            print(f"{name:20s} {st}")


if __name__ == "__main__":
    main()
