# Reproducing the study

Every number in the preprint regenerates from this repository with **zero API calls and zero cost**. CI does exactly this on every push.

## 1. Requirements

Python 3.9+ and:

```bash
pip install -r requirements.txt   # numpy, matplotlib, fpdf
```

## 2. One command

```bash
make all
```

which runs, in order:

| Step | Command | Output |
|------|---------|--------|
| Analysis | `python3 analysis/analise.py` | `analysis/results/resultado_analise.json` + stdout stats |
| Verification | `python3 analysis/permutacao.py` | PASS/FAIL report + `analysis/results/permutacao*_reproducao.json` |
| Figure | `python3 figures/figura.py` | `figures/figura_sotaque_drainer.png` |
| Paper | `python3 paper/paper_drainer.py` | `paper/paper_drainer.pdf` |

Any step that fails exits non-zero. No step writes outside the repository.

## 3. What is verified

`analysis/permutacao.py` is the reproduction gate:

1. Recomputes **every published mean and CLES** from the raw datasets and compares with the canonical `analysis/results/permutacao*.json` at tolerance 1e-9 (15/15 must match).
2. Reruns the permutation tests with fixed seeds (42 / 43) and compares the headline p-values with the published permutation floor.
3. Exits non-zero if (1) fails. CI (`.github/workflows/ci.yml`) blocks pushes that break reproducibility.

Documented divergences for weak-signal p-values are expected and listed in [METHODOLOGY.md §5.3](METHODOLOGY.md) — the published files are historical artifacts of the preprint and are never overwritten by the verifier; the seeded reference run is written side-by-side as `permutacao*_reproducao.json`.

## 4. Re-collecting from the chain (optional)

If you want to rebuild the datasets from scratch (network required, still free):

```bash
make collect   # ~30-60 min against the public Blockscout v2 API
```

Order and logic: `coleta.py` → `coleta2.py` → `coleta3.py` → `conserta.py` → `controle_comum.py` (see `collection/README.md`). Note that live addresses change over time, so a fresh collection will not be byte-identical to the frozen snapshot; the published analysis always uses the datasets in `data/`.

## 5. CI

`.github/workflows/ci.yml` runs `make all` on every push and pull request, on `ubuntu-latest` with Python 3.11. The badge at the top of the README is that run.

## 6. Expected runtime (local & CI)

| Step | Time |
|------|------|
| `analysis` | ~5 s |
| `verify` (permutations, seeded) | ~10 s |
| `figure` | ~3 s |
| `paper` | ~2 s |
