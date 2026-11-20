# İrisya Clinic

Static marketing site for İrisya Clinic (eye colour change in Istanbul), plus the scripts that produced its images and hero film.

## Structure

| Folder | What it is |
| --- | --- |
| `irisya-clinic/` | The website: `index.html`, `assets/css/style.css`, `assets/js/main.js`. No build step. |
| `irisya-tools/` | Python scripts that generate and process the site's images (Higgsfield jobs in `hf/`). |
| `hero-film/irisya/` | Script and prompts for the hero film. |
| `backups/` | Code snapshots taken before the two redesigns. |
| `vors-dental-clinic/` | Reference copy of another site used during design. |

## Run locally

Python 3 is enough:

```
cd irisya-clinic
python -m http.server 5510
```

Then open http://localhost:5510. On Windows you can double-click `siteyi-ac.bat`.

## Missing media

The project was restored from session history on 2026-11-20 and its images and videos are not in the repository yet.
`KURTARMA-NOTU.md` lists every missing file under `irisya-clinic/assets/img/`. Until they are added, photo areas render empty.
