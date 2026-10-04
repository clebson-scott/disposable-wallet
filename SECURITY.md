# Security policy

This repository is **defensive security research**. There is nothing here to attack: no exploits, no drainer code, no victim data.

## Reporting a vulnerability in this repository

If you find a bug that could produce wrong statistics (which we consider a correctness vulnerability):

1. Open a *Bug report* issue describing the affected script and the expected vs actual output.
2. If it affects published numbers, mark it with the `published-numbers` label — those get priority.

## Scope & ethics

- We do **not** publish tools that harm users. Feature collectors read public chain data through public APIs.
- Addresses in the datasets come from public blockchains and public vendor incident reports. If you believe an address is wrongly labeled, open a *Data report* issue with evidence; wrong labels are corrected with a documented dataset note.
- Responsible disclosure first: findings that could affect real users are coordinated with affected vendors before publication.

## Supported version

The `main` branch is the supported version. Published artifacts are frozen in `analysis/results/` and on Zenodo (DOI 10.5281/zenodo.23136779).
