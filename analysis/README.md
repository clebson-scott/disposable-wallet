# Analysis

Turns the frozen datasets into every published number. Runs anywhere, no network.

## Scripts

| Script | What it does | Writes |
|--------|--------------|--------|
| `analise.py` | Fusion + dedupe, empty-wallet chi², Mann-Whitney per feature, logistic 5-fold CV (seed 42) | `results/resultado_analise.json` |
| `permutacao.py` | **Reproduction gate**: recomputes every published mean/CLES (1e-9 tolerance), reruns seeded permutation tests | `results/permutacao*_reproducao.json` |

## results/

| File | Status |
|------|--------|
| `resultado_analise.json` | regenerated identically by `analise.py` |
| `permutacao.json`, `permutacao_comum.json` | **published artifacts** (cited by the preprint, frozen) |
| `permutacao_reproducao.json`, `permutacao_comum_reproducao.json` | seeded reference run, written by `permutacao.py` |

The published artifact and the reference run agree on every mean, every CLES (1e-9) and every headline p-value; weak-signal p-value divergences are documented in `docs/METHODOLOGY.md` §5.3.

Run: `make analysis && make verify` (CI does this on every push).
