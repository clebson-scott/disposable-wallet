# Data dictionary

One JSON object per line (JSONL) in every `data/dataset*.jsonl` file. One record = one Ethereum address.

## Identity & screening fields (all records)

| Field | Type | Definition |
|-------|------|-----------|
| `addr` | string | Ethereum address, lowercase hex, primary key (dedupe: last write wins) |
| `label` | string | `scam` \| `honesto` (rich honest control) \| `comum` (matched common control) |
| `is_contract` | bool | Always `false` in the datasets — contracts are skipped at collection time |
| `sem_tx` | bool | `true` when the address has no retrievable transactions (the "empty wallet" flag) |
| `bs_scam_flag` | bool | Public "is scam" flag reported by the Blockscout instance (independent of our labels) |

## Fields for addresses without history (`sem_tx: true`)

| Field | Type | Definition |
|-------|------|-----------|
| `balance_eth` | float | ETH balance at collection time |
| `has_ens` | bool | ENS domain name present |
| `tx_count` | int | API-reported tx count (0 for these records) |
| `token_transfers` | int | API-reported token transfer count |
| `gas_usage` | int | API-reported gas used (gwei) |

## Behavioral fields (addresses with history, the "accent" features)

| Field | Type | Definition |
|-------|------|-----------|
| `n_tx` | int | Number of transactions analyzed (last 50) |
| `mediana_valor` | float | Median ETH value of those txs |
| `max_valor` | float | Maximum ETH value |
| `log_mediana` | float | log10(`mediana_valor`); 0-value → -20 |
| `log_max` | float | log10(`max_valor`); 0-value → -20 |
| `frac_enviadas` | float | Fraction of txs sent by the address |
| `contrapartes_unicas` | int | Unique counterparties (to when sending, from when receiving) |
| `frac_transferencia_pura` | float | Fraction of txs with `raw_input == "0x"` (plain value transfers) |
| `frac_revert` | float | Fraction of failed txs |
| `tx_por_hora` | float | n_tx / hours between first and last observed tx (0 if single tx) |

## Seed files (`data/seed/`)

| File | Content |
|------|---------|
| `scam_addrs.json` | 2,530 raw addresses from the ScamSniffer incident-report list (before dedupe and API filtering) |
| `control_candidates.json` | 818 control candidates from Etherscan lists |

## Files & provenance

| File | Group | Collected by |
|------|--------|--------------|
| `data/dataset.jsonl` | scam + honesto, batch 1 | `collection/coleta.py` |
| `data/dataset2.jsonl` | batch 2 (dedupe against batch 1) | `collection/coleta2.py` |
| `data/dataset3.jsonl` | batch 3 (dedupe against 1+2) | `collection/coleta3.py` |
| `data/dataset_comuns.jsonl` | matched common (label `comum`) | `collection/controle_comum.py` |

API: public Blockscout v2 (`eth.blockscout.com`), October 2026. Counts and values change over time for live addresses; the datasets in this repository are the frozen snapshot used by the published analysis.
