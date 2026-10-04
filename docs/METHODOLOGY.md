# Methodology

This document explains exactly how the study was built. Everything here is verifiable: each claim points to a file in this repository or to a public API.

## 1. Research question

Do addresses used by wallet-drainer operations (phishing/drainer campaigns) carry a measurable *behavioral signature* on Ethereum, observable from public chain data alone, before and during their operation?

## 2. Sample construction

| Group | n | Source | Notes |
|-------|---|--------|-------|
| Scam (drainer) addresses | 757 unique | ScamSniffer incident reports (2023-2024 phishing/drainer address list) | Seeds in `data/seed/scam_addrs.json` (2,530 raw entries) |
| Rich honest controls | 707 unique | Etherscan top-holder/active lists | Seeds in `data/seed/control_candidates.json` (818 candidates) |
| Matched common controls | 264 | Live sampling of Blockscout transaction feed | Senders of plain ETH transfers of 0.001-2 ETH, recent txs |

- The three collection batches (`collection/coleta.py`, `coleta2.py`, `coleta3.py`) fetch the same per-address features from the public **Blockscout v2 API** and dedupe by address (`addr` key, last batch wins).
- `collection/conserta.py` repairs raw counter fields after an API counter bug discovered mid-collection (documented in `collection/README.md`).
- `collection/controle_comum.py` builds the *matched common* group: EOAs that recently sent a simple ETH transfer — deliberately ordinary users. **Declared caveat:** sampling from plain-ETH senders mechanically inflates their `frac_transferencia_pura`, which is discussed in the paper and in [FINDINGS.md](FINDINGS.md).

## 3. Features (8 + screening fields)

For every address with transaction history, the collectors compute:

| Feature | Definition |
|---------|------------|
| `log_mediana` | log10 of the median ETH value of the last 50 txs (0 or negative value → -20) |
| `log_max` | log10 of the maximum ETH value |
| `frac_enviadas` | fraction of txs where the address is the sender |
| `contrapartes_unicas` | number of unique counterparties |
| `frac_transferencia_pura` | fraction of txs with empty `raw_input` (plain value transfers) |
| `frac_revert` | fraction of failed (reverted) txs |
| `tx_por_hora` | txs per hour across the observed time span |
| `balance_eth` | current ETH balance |

Screening fields (`sem_tx`, `is_contract`, `has_ens`, `bs_scam_flag`, `tx_count`, `token_transfers`, `gas_usage`) are defined in [DATA_DICTIONARY.md](DATA_DICTIONARY.md).

## 4. Statistics

All implementations are dependency-light (numpy only) and live in `analysis/`:

1. **Empty-wallet test** — 2x2 chi-square without continuity correction on `sem_tx || (balance==0 && no tx)`, p-value via erfc approximation for 1 dof (`analysis/analise.py`, section [1]).
2. **Per-feature accent** — Mann-Whitney U with tie-corrected ranks and tie-corrected sigma; medians and z-values printed per feature (`analysis/analise.py`, section [2]).
3. **Classifier** — logistic regression (gradient descent, standardized features, seed 42), stratified 5-fold CV, accuracy + AUC computed pairwise (`analysis/analise.py`, section [3]).
4. **Effect sizes** — CLES (Common Language Effect Size) = P(scam value > control value) + 0.5·P(tie), computed in O(n log n) via ranks (`analysis/permutacao.py`).
5. **Permutation tests** — label permutations with fixed seeds (2,000 for scam-vs-honest, 1,000 for scam-vs-common), one-sided in the observed direction, p = (count+1)/(N+1) (`analysis/permutacao.py`).

## 5. Honest caveats (declared, not hidden)

1. **Selection bias (rich controls).** The honest controls of the headline comparison are active/rich Etherscan wallets. This inflates the separation (notably `balance_eth`, `tx_por_hora`). The *matched common* control was built precisely to test whether the accent survives among ordinary users — it does for the core features (p < 0.001), while `balance_eth` differences are expected to shrink and are treated as a rich-control artifact.
2. **Common-control sampling.** `controle_comum.py` samples senders of plain ETH transfers, which mechanically raises their `frac_transferencia_pura` (median ~0.85). This is disclosed in the paper; the accent's other components do not depend on it.
3. **Permutation p-values of weak signals.** The published `permutacao*.json` files were produced by an ad-hoc session whose script was not archived. `analysis/permutacao.py` is the seeded reference implementation: it reproduces every published mean and CLES to 1e-9 and every headline ("accent") p-value at the permutation floor 1/(N+1). For weak signals, p-values may differ from the published files (e.g. `balance_eth` scam-vs-honest: published 0.0390, reference implementation 0.0005 — consistent with the observed CLES of 0.365 at ~7 sigma). Published files are kept unchanged as the historical artifact cited by the preprint; both versions are side-by-side in `analysis/results/`.
4. **No temporal ground truth.** We observe drainer addresses as flagged *after* incidents; the "before/during" framing is an inference from their behavior state at collection time, not a tracked longitudinal history.
5. **Defensive scope.** No exploit, no first-strike, no deanonymization. Addresses are public.

## 6. Relation to ZEUS GUARD

This study provides the empirical motivation for [ZEUS GUARD](https://github.com/clebson-scott/zeus-guard), a pre-transaction firewall: if drainers carry a measurable signature, a local risk engine can score counterparties before a signature is requested. The classifier here is a research instrument, not the product.
