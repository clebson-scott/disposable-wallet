#!/usr/bin/env python3
"""Figura publicavel: o sotaque on-chain dos drainers (3 grupos)."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED = DATA / "seed"
RESULTS = ROOT / "analysis" / "results"
FIGURES = ROOT / "figures"
PAPERS = ROOT / "paper"

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight",
    "axes.titlesize": 9.5, "axes.labelsize": 8.5,
})

regs = {}
for arq in [DATA / "dataset.jsonl", DATA / "dataset2.jsonl", DATA / "dataset3.jsonl", DATA / "dataset_comuns.jsonl"]:
    try:
        for l in open(arq):
            r = json.loads(l)
            regs[r["addr"]] = r
    except FileNotFoundError:
        pass
data = list(regs.values())

grupos = {
    "Drainers (scam)": [r for r in data if r["label"] == "scam"],
    "Controle rico": [r for r in data if r["label"] == "honesto"],
    "Controle comum": [r for r in data if r["label"] == "comum"],
}
cores = {"Drainers (scam)": "#c0392b", "Controle rico": "#2471a3", "Controle comum": "#1e8449"}

# Painel A: barras % carteira vazia
fig, axes = plt.subplots(2, 3, figsize=(10, 6.2))
fig.suptitle("On-chain accent of wallet drainers — 1,464+ Ethereum addresses", fontsize=11, y=0.99)

ax = axes[0][0]
labels, vals, ns = [], [], []
for g, rs in grupos.items():
    if not rs: continue
    vaz = sum(bool(r.get("sem_tx")) or (r.get("balance_eth", 0) == 0 and not r.get("n_tx")) for r in rs)
    labels.append(g); vals.append(vaz / len(rs) * 100); ns.append(len(rs))
b = ax.bar(range(len(vals)), vals, color=[cores[l] for l in labels], width=0.55)
for i, (v, n) in enumerate(zip(vals, ns)):
    ax.text(i, v + 2, f"{v:.0f}%\nn={n}", ha="center", fontsize=7.5)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=7)
ax.set_ylabel("% carteira vazia / sem tx")
ax.set_ylim(0, 62)
ax.set_title("A. Endereço descartável", loc="left")

# Painel B-F: distribuicoes (so com historico completo)
FEATS = [("contrapartes_unicas", "B. Contrapartes únicas (50 tx)", 35),
         ("frac_transferencia_pura", "C. Fração de tx de ETH puro", 1.05),
         ("log_max", "D. log10(valor máx. tx, ETH)", 1),
         ("tx_por_hora", "E. Ritmo: tx por hora", 30),
         ("frac_enviadas", "F. Fração enviada (vs recebida)", 1.05)]

pos = [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
for (f, titulo, xmax), (i, j) in zip(FEATS, pos):
    ax = axes[i][j]
    for g, rs in grupos.items():
        v = [r[f] for r in rs if not r.get("sem_tx") and f in r]
        if not v: continue
        bins = np.linspace(0, xmax, 28)
        ax.hist(np.clip(v, 0, xmax), bins=bins, density=True, alpha=0.55,
                color=cores[g], label=f"{g} ({len(v)})", edgecolor="none")
    ax.set_title(titulo, loc="left")
    ax.set_yticks([])
    if f == "tx_por_hora":
        ax.set_yscale("log")
        ax.set_ylabel("densidade (log)")
    for s in ["axes.titlesize"]: pass
    ax.tick_params(labelsize=7)

axes[1][2].legend(fontsize=6.5, frameon=False)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(FIGURES / "figura_sotaque_drainer.png", dpi=200)
print("figura salva: figura_sotaque_drainer.png")
