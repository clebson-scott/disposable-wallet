# Contributing

Thanks for wanting to improve an open-science security study. Everything here is defensive research.

## Ways to contribute

- **Reproduce**: run `make all` on your machine and open a question if any step fails or diverges.
- **New control groups**: better-matched controls are the single most valuable extension (see `docs/METHODOLOGY.md` §5). Propose the sampling logic in an issue first.
- **New features**: behavioral features must be computable from public chain data only, with no API keys.
- **Data reports**: if you find a mislabeled address, open a *Data report* issue with the address and evidence.

## Ground rules

1. **Defensive scope only.** No exploits, no attack tooling, no deanonymization attempts, no first-strike. This repo studies attacker *behavior* to protect users.
2. **Numbers must regenerate.** Every claim must come from a script in this repo. `make all` and CI must pass.
3. **No silent overwrites of published artifacts.** `analysis/results/permutacao*.json` are the published preprint artifacts. New analyses write new files; corrections get documented in `docs/METHODOLOGY.md`.
4. **Declare your bias.** If your control sampling has a mechanical quirk (like ours do — we declare them), write it down.

## Workflow

1. Fork, branch (`analysis/your-extension`).
2. `make all` green.
3. PR following `.github/PULL_REQUEST_TEMPLATE.md`.
