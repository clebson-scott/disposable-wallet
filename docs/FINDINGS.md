# Findings

Every number below regenerates from this repository. Run `make analysis` and `make verify` and compare with `analysis/results/`.

## Sample

| Quantity | Value | Source |
|----------|-------|--------|
| Unique wallets (scam + rich honest) | 1,464 (757 scam / 707 honest) | `analysis/analise.py` stdout |
| Matched common controls | 264 | `data/dataset_comuns.jsonl` |
| With transaction history | 389 scam / 622 honest | `analysis/permutacao.py` stdout |

## 1. Disposability — the empty wallet

| Metric | Scam | Rich honest | Matched common |
|--------|------|-------------|----------------|
| Empty / no tx | **48.5%** | 9.5% | 2.2% |

chi² = 266.7 (scam vs rich honest), p ≈ 6e-60. Stored in `analysis/results/resultado_analise.json` → `vazia_scam_pct`, `vazia_hon_pct`, `chi2`.

## 2. The accent (scam vs rich honest, wallets with history)

| Feature | Mean scam | Mean honest | CLES | p (permutation, published) |
|---------|-----------|-------------|------|---------------------------|
| log_mediana | -9.59 | -13.04 | 0.622 | 0.00050 |
| log_max | -1.61 | -5.24 | 0.724 | 0.00050 |
| frac_enviadas | 0.641 | 0.803 | 0.317 | 0.00050 |
| contrapartes_unicas | 16.95 | 10.26 | 0.654 | 0.00050 |
| frac_transferencia_pura | 0.544 | 0.381 | 0.637 | 0.00050 |
| tx_por_hora | 1.10 | 19.27 | 0.313 | 0.00050 |
| balance_eth | 0.028 | 426.13 | 0.365 | 0.0390 (see caveat) |

All means and CLES reproduce to 1e-9 (`analysis/permutacao.py` verifies). Mann-Whitney z-values printed by `analysis/analise.py`. The `balance_eth` p-value caveat is documented in [METHODOLOGY.md §5.3](METHODOLOGY.md).

## 3. The accent vs matched common users (scam vs comum)

| Feature | Mean scam | Mean common | CLES | p (permutation, published) |
|---------|-----------|-------------|------|---------------------------|
| log_mediana | -9.59 | -3.30 | 0.337 | 0.0010 |
| log_max | -1.61 | -0.78 | 0.559 | 0.0080 |
| contrapartes_unicas | 16.95 | 14.64 | 0.553 | 0.0290 |
| frac_transferencia_pura | 0.544 | 0.849 | 0.253 | 0.0010 |
| tx_por_hora | 1.10 | 38.87 | 0.297 | 0.0010 |
| balance_eth | 0.028 | 1537.96 | 0.495 | 0.0010 |

Core rhythm features (`tx_por_hora`, `log_mediana`, `frac_transferencia_pura`) keep p ≤ 0.001 even against ordinary users — the accent is not just "drainers are poor".

## 4. Classifier

| Metric | vs rich honest | vs matched common |
|--------|----------------|------------------|
| Accuracy (5-fold CV, chance level in parentheses) | 70.0% (61.5%) | 74.6% (59.6%) |
| AUC | 0.784 | — |

Logistic regression on 8 standardized features, seed 42, stratified 5-fold. The honest-control run is stored in `analysis/results/resultado_analise.json` (`acuracia_cv`, `auc_cv`); the common-control run is printed by `analysis/analise.py` section [6] (stdout only, keeps the published JSON byte-identical). Most-loaded coefficients printed by `analysis/analise.py` section [4].

## 5. Reproduction status

`analysis/permutacao.py` (also run by CI):

- means & CLES vs published files: **15/15 PASS at 1e-9**
- headline permutation p-values: **identical** (floor 1/(N+1))
- weak-signal p-values: documented divergences (see [METHODOLOGY.md §5.3](METHODOLOGY.md)); side-by-side files: `permutacao*.json` (published) and `permutacao*_reproducao.json` (seeded reference run)
