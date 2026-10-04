# The Disposable Wallet

Behavioral signatures of cryptocurrency **drainer addresses on Ethereum**: an empirical study of 1,464 wallets.

**Preprint (open access, CC-BY 4.0):** DOI [10.5281/zenodo.23136779](https://doi.org/10.5281/zenodo.23136779)

> Do wallet drainers carry a measurable on-chain behavioral signature before and during their operation?

## Key findings

1. **Disposability** — 48.5% of malicious addresses are empty or transaction-less, vs 9.5% of rich honest controls and 2.2% of matched common users (chi-square 266.7, p ~ 6e-60).
2. **The accent** — drainers transact with more unique counterparties (~17 vs 10-15), at a near-dormant rhythm (~1.1 tx/h vs 19-39), with larger maximum values; all differences survive permutation tests (p < 0.001).
3. **Prediction** — a logistic classifier on 8 behavioral features identifies malicious addresses with 70.0% accuracy (AUC 0.784) against rich controls and 74.0% against matched common controls, 5-fold CV.

## Reproduce

Every number costs zero to reproduce (public Blockscout v2 API):

```bash
python3 coleta.py && python3 coleta2.py && python3 coleta3.py && python3 controle_comum.py
python3 analise.py && python3 figura.py && python3 paper_drainer.py
```

## Contents

| File | What it is |
|---|---|
| `paper_drainer.pdf` | Preprint (also on Zenodo) |
| `figura_sotaque_drainer.png` | Figure 1 (6 panels) |
| `dataset*.jsonl` | Raw per-address features (1,464 + 264 wallets) |
| `coleta*.py`, `controle_comum.py` | Collectors (Blockscout v2) |
| `analise.py`, `permutacao*.json`, `resultado_analise.json` | Statistics |
| `figura.py`, `paper_drainer.py` | Figure and paper generators |

## Ethics

Defensive research. All addresses are public (blockchain) or from vendor incident reports. Motivating application: [ZEUS GUARD](https://github.com/clebson-scott/zeus-guard), the open-source pre-transaction firewall.

## Author

**Clebson Campos de Araujo** — ZEUS GUARD Security Lab (independent)

## License

CC-BY 4.0 (matching the Zenodo deposit)
