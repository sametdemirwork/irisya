"""Generate İrisya site images on Higgsfield.

Reads jobs.json (list of {name, model, prompt, aspect_ratio, quality?, image?, extra?}),
runs each job with the `higgsfield` CLI (--wait --json), downloads the result to raw/<name>.png
and writes raw/<name>.json with the job metadata. Existing raw files are skipped unless --force.

Usage:
  python gen.py                 # every job that has no raw file yet
  python gen.py story-2 shade-1 # only these names
  python gen.py --force shade-1 # regenerate
  python gen.py -j 6            # concurrency (default 5)
"""
import json
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
# call the native binary directly so prompts never pass through cmd.exe quoting
HF = HERE / "bin" / "hf.exe"  # copy of npm's vendor/hf.exe (Store Python cannot see AppData\Roaming\npm)
HF = str(HF) if HF.exists() else "higgsfield"
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)


def run(job, force=False):
    name = job["name"]
    out = RAW / f"{name}.png"
    if out.exists() and not force:
        return name, "skip", 0
    cmd = [HF, "generate", "create", job["model"], "--prompt", job["prompt"]]
    if job.get("aspect_ratio"):
        cmd += ["--aspect_ratio", job["aspect_ratio"]]
    if job.get("quality"):
        cmd += ["--quality", job["quality"]]
    if job.get("image"):
        img = job["image"]
        if not img.startswith(("http", "/")) and ":" not in img and len(img) != 36:
            img = str(RAW / img)
        cmd += ["--image", img]
    for k, v in (job.get("extra") or {}).items():
        cmd += [f"--{k}", str(v)]
    cmd += ["--wait", "--wait-timeout", "15m", "--json"]
    t0 = time.time()
    for attempt in range(2):
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        txt = p.stdout.strip()
        try:
            res = json.loads(txt[txt.index("["):])
            res = res[0] if isinstance(res, list) else res
        except Exception:
            res = None
        if res and res.get("status") == "completed" and res.get("result_url"):
            break
        err = (p.stderr or txt)[-600:]
        if attempt == 1:
            (RAW / f"{name}.err").write_text(err, encoding="utf-8")
            return name, f"FAIL {err.strip()[:200]}", time.time() - t0
    urllib.request.urlretrieve(res["result_url"], out)
    (RAW / f"{name}.json").write_text(json.dumps({"job": job, "result": res}, indent=1, ensure_ascii=False), encoding="utf-8")
    return name, "ok", time.time() - t0


def main():
    args = sys.argv[1:]
    force = "--force" in args
    conc = 5
    if "-j" in args:
        conc = int(args[args.index("-j") + 1])
        del args[args.index("-j"):args.index("-j") + 2]
    names = [a for a in args if not a.startswith("-")]
    jobs = json.loads((HERE / "jobs.json").read_text(encoding="utf-8"))
    if names:
        jobs = [j for j in jobs if j["name"] in names]
    # jobs that reference another raw image must wait for it
    first = [j for j in jobs if not (j.get("image") and not (RAW / j["image"]).exists() and j["image"].endswith(".png"))]
    later = [j for j in jobs if j not in first]
    for batch in (first, later):
        with ThreadPoolExecutor(conc) as ex:
            futs = [ex.submit(run, j, force) for j in batch]
            for f in as_completed(futs):
                n, st, dt = f.result()
                print(f"{n:24s} {st} {dt:5.0f}s", flush=True)


if __name__ == "__main__":
    main()
