# Collection pipeline

Talks to the public **Blockscout v2 API** (`eth.blockscout.com`). No API keys. Each collector writes JSONL into `data/`.

## Order

```
coleta.py         batch 1: scam seeds + control candidates -> data/dataset.jsonl
coleta2.py        batch 2: dedupes against batch 1       -> data/dataset2.jsonl
coleta3.py        batch 3: dedupes against batches 1+2    -> data/dataset3.jsonl
conserta.py       repairs raw counter fields             -> rewrites data/dataset.jsonl
controle_comum.py matched common-control sampling        -> data/dataset_comuns.jsonl
```

Run everything: `make collect` (~30-60 min, 6 parallel workers, public rate limits respected with retries).

## The counter-fix story (transparency)

Mid-collection, the API's transaction-count fields were found inconsistent with the listed transactions (counter bug). `conserta.py` recomputes the raw counters (`tx_count`, `token_transfers`, `gas_usage`) consistently from the transaction lists, and the analysis flags empty wallets with `sem_tx` (never with the raw counters alone). This is the fix mentioned in the study notes: numbers published after the fix, verified by `analysis/permutacao.py`.

## Sampling decisions (declared)

- EOAs only (`is_contract` skipped).
- Last 50 transactions per address.
- `controle_comum.py` samples senders of plain ETH transfers (0.001-2 ETH): ordinary users by construction, with the declared side-effect on `frac_transferencia_pura` (see `docs/METHODOLOGY.md` §5.2).
