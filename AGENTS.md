# AGENTS.md — Base44 dev notes for "The Disposable Wallet"

## What this project is
A **reproducible Python research study** (not a web app). It regenerates
statistical results, a figure, and a PDF preprint from local JSONL datasets.
There is no web framework, no server, no database, and **no external
credentials** — every number comes from `data/dataset*.jsonl` with zero API
calls.

## Running it here
`docker compose -f docker-compose.base44.yml up -d --build` builds the image
(`Dockerfile.base44`: python:3.11-slim + libglib/pango/cairo for matplotlib +
numpy/matplotlib/fpdf from requirements.txt), then the service command runs
`make all` and serves the repo root on port 3000 via `python3 -m http.server`.

- `make all` = analysis → verify (permutation tests) → figure → paper.
- The permutation step (`analysis/permutacao.py`) raises `SystemExit(1)` if any
  published mean/CLES fails to reproduce at 1e-9; a clean dataset always PASSes.
- `index.html` at the repo root is the results dashboard shown in the preview.

## No secrets
No environment variables or external credentials are required to boot or run
the analysis. `make collect` (re-collecting from the Blockscout v2 API) is
optional, network-bound, and not part of the preview flow.

## Verifying it works
- `docker compose -f docker-compose.base44.yml ps` shows the `web` service healthy.
- `curl -s http://localhost:3000/` returns the dashboard HTML.
- `curl -s http://localhost:3000/analysis/results/resultado_analise.json` returns
  the regenerated analysis JSON.
- The preview shows the dashboard with the embedded Figure 1 and links to the PDF.

## Editing
- Changes to `index.html` appear on browser refresh (no live-reload server).
- Changes to analysis/figure/paper scripts require a service restart to re-run
  `make all`: `docker compose -f docker-compose.base44.yml restart web`, then
  `reload_preview`.
