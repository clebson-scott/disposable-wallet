# Data

Frozen snapshot used by the published analysis (October 2026). One JSON object per line; see [docs/DATA_DICTIONARY.md](../docs/DATA_DICTIONARY.md) for every field.

## Files

| File | Records | Group | Collected by |
|------|---------|-------|--------------|
| `dataset.jsonl` | batch 1 | 757 scam + honesto | `collection/coleta.py` |
| `dataset2.jsonl` | batch 2 | dedupe against batch 1 | `collection/coleta2.py` |
| `dataset3.jsonl` | batch 3 | dedupe against batches 1+2 | `collection/coleta3.py` |
| `dataset_comuns.jsonl` | 264 | matched common (`comum`) | `collection/controle_comum.py` |
| `seed/scam_addrs.json` | 2,530 raw | ScamSniffer incident list | — |
| `seed/control_candidates.json` | 818 candidates | Etherscan lists | — |

Dedup key: `addr` (lowercase). When batches disagree, the last batch wins — same rule as `analysis/analise.py`.

## Why a frozen snapshot

Live addresses change (balances move, new txs arrive). The published numbers are computed from *this* snapshot; re-collecting produces a new, similar-but-not-identical dataset (see [docs/REPRODUCING.md §4](../docs/REPRODUCING.md)).

## Provenance

- **Scam seeds:** public ScamSniffer incident-report address list (2,530 entries → 757 unique after dedupe + API filtering).
- **Rich honest seeds:** Etherscan top/active wallet lists (818 candidates → 707 unique).
- **Common controls:** live sampling of the public Blockscout transaction feed (senders of plain 0.001-2 ETH transfers).
- All per-address features come from the public Blockscout v2 API. No keys, no paid endpoints.
