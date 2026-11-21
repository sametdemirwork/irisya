# İrisya Clinic

Static marketing site for İrisya Clinic (eye colour change in Istanbul), plus the scripts that produced its images and hero film.

## Structure

| Folder | What it is |
| --- | --- |
| `irisya-clinic/` | The website: `index.html`, `assets/css/style.css`, `assets/js/main.js`. No build step. |
| `irisya-tools/` | Python scripts that generate and process the site's images (Higgsfield jobs in `hf/`). |
| `hero-film/irisya/` | Script and prompts for the hero film. |

## Run locally

Python 3 is enough:

```
cd irisya-clinic
python -m http.server 5510
```

Then open http://localhost:5510. On Windows you can double-click `siteyi-ac.bat`.

## Media

The project was restored from session history on 2026-11-20. Its photos were then rebuilt from the original
Higgsfield generations (`irisya-tools/hf/sources.json`, `fetch.py`), and the image edits that the Higgsfield
history no longer lists were redone locally (`irisya-tools/hf/recolour.py`). The hero film is cut from six Kling 4.0
clips still held in the Higgsfield account (`hero-film/irisya/build.py fetch`, then `build.py`).
`KURTARMA-NOTU.md` has the details. Still missing: the logo files under `irisya-clinic/assets/img/brand/`, which come
from the supplied logo artwork via `irisya-tools/brand.py`.
