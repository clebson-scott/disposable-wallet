#!/usr/bin/env python3
"""Analise estatistica do 'sotaque on-chain' de drainers vs honestos.
Fusao dos lotes 1-3, dedupe, features, testes e classificador."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED = DATA / "seed"
RESULTS = ROOT / "analysis" / "results"
FIGURES = ROOT / "figures"
PAPERS = ROOT / "paper"

import json, math
import numpy as np

regs = {}
for arq in [DATA / "dataset.jsonl", DATA / "dataset2.jsonl", DATA / "dataset3.jsonl"]:
    try:
        for l in open(arq):
            r = json.loads(l)
            regs[r["addr"]] = r  # ultima versao vence
    except FileNotFoundError:
        pass

data = list(regs.values())
scam = [r for r in data if r["label"] == "scam"]
hon = [r for r in data if r["label"] == "honesto"]
print(f"Fusao: {len(data)} carteiras unicas | scam: {len(scam)} | honesto: {len(hon)}")

# --- Metrica principal: carteira vazia / sem transacao ---
def vazia(r):
    return bool(r.get("sem_tx")) or (r.get("balance_eth", 0) == 0 and not r.get("n_tx"))

p_scam = sum(vazia(r) for r in scam) / len(scam) * 100
p_hon = sum(vazia(r) for r in hon) / len(hon) * 100
print(f"\n[1] CARTEIRA VAZIA/SEM TX: golpistas {p_scam:.1f}% vs honestos {p_hon:.1f}%")

# teste qui-quadrado 2x2
a = sum(vazia(r) for r in scam); b = len(scam) - a
c = sum(vazia(r) for r in hon);  d = len(hon) - c
n = a + b + c + d
chi2 = n * (a * d - b * c) ** 2 / ((a + b) * (c + d) * (a + c) * (b + d))
# p-valor via sobrevivencia da chi2 com 1 gl (usando gammainc)
from math import erfc
p_chi = erfc(math.sqrt(chi2 / 2))  # aproximacao: p = erfc(sqrt(chi2/2)) para 1 gl
print(f"    chi2={chi2:.1f}, p~{p_chi:.2e} | n_scam_vazia={a}, n_hon_vazia={c}")

# --- Features dos que TEM tx (o 'sotaque') ---
FEATS = ["log_mediana", "log_max", "frac_enviadas", "contrapartes_unicas",
         "frac_transferencia_pura", "frac_revert", "tx_por_hora", "balance_eth"]
scam_tx = [r for r in scam if not r.get("sem_tx") and all(f in r for f in FEATS)]
hon_tx = [r for r in hon if not r.get("sem_tx") and all(f in r for f in FEATS)]
print(f"\nCom historico: scam {len(scam_tx)} | honesto {len(hon_tx)}")

def mediana(v):
    v = sorted(v); n = len(v)
    return (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)

# Mann-Whitney U (implementacao exata via rank para n grande -> normal aprox)
def mannwhitney(x, y):
    from statistics import NormalDist
    nx, ny = len(x), len(y)
    allv = [(v, 0) for v in x] + [(v, 1) for v in y]
    allv.sort(key=lambda t: t[0])
    ranks = [0.0] * (nx + ny); i = 0
    while i < len(allv):
        j = i
        while j < len(allv) and allv[j][0] == allv[i][0]:
            j += 1
        r = (i + j + 1) / 2  # rank medio do bloco de empates
        for k in range(i, j):
            ranks[k] = r
        i = j
    U = sum(ranks[:nx]) - nx * (nx + 1) / 2
    mu = nx * ny / 2
    # correcao de empates na sigma
    allvals = [t[0] for t in allv]
    tie_counts = {}
    for v in allvals: tie_counts[v] = tie_counts.get(v, 0) + 1
    tie_term = sum(t ** 3 - t for t in tie_counts.values())
    N = nx + ny
    sigma = math.sqrt(nx * ny / 12 * ((N + 1) - tie_term / (N * (N - 1))))
    z = (U - mu) / sigma if sigma > 0 else 0
    p = 2 * (1 - NormalDist().cdf(abs(z)))
    return U, z, p

print("\n[2] SOTAQUE POR FEATURE (Mann-Whitney U, comparacao scam vs honesto):")
sig = []
for f in FEATS:
    xs = [r[f] for r in scam_tx]
    ys = [r[f] for r in hon_tx]
    U, z, p = mannwhitney(xs, ys)
    ms, mh = mediana(xs), mediana(ys)
    mark = " ***" if p < 0.001 else (" **" if p < 0.01 else (" *" if p < 0.05 else ""))
    print(f"  {f:26s} scam={ms:>10.3f} | honesto={mh:>10.3f} | z={z:6.2f} p={p:.2e}{mark}")
    if p < 0.05: sig.append((f, p, "scam maior" if ms > mh else "hon maior"))

# --- Classificador: o sotaque previu drainer ANTES da label? ---
# Regressao logistica simples (gradiente descendente) com validacao cruzada 5-fold estratificada
Xs = np.array([[r[f] for f in FEATS] for r in scam_tx if all(f in r for f in FEATS)])
Xh = np.array([[r[f] for f in FEATS] for r in hon_tx if all(f in r for f in FEATS)])
X = np.vstack([Xs, Xh]); y = np.concatenate([np.ones(len(Xs)), np.zeros(len(Xh))])
# normaliza
mu = X.mean(0); sd = X.std(0) + 1e-9
Xn = (X - mu) / sd
Xn = np.hstack([np.ones((len(Xn), 1)), Xn])

rng = np.random.default_rng(42)
idx = rng.permutation(len(Xn))
Xn, y = Xn[idx], y[idx]

def logreg_fit(X, y, iters=4000, lr=0.1):
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ w))
        w -= lr * X.T @ (p - y) / len(y)
    return w

k = 5
folds = np.array_split(np.arange(len(y)), k)
accs, aucs = [], []
for i in range(k):
    te = folds[i]; tr = np.concatenate([folds[j] for j in range(k) if j != i])
    w = logreg_fit(Xn[tr], y[tr])
    p = 1 / (1 + np.exp(-Xn[te] @ w))
    pred = (p >= 0.5).astype(int)
    accs.append((pred == y[te]).mean())
    # AUC
    pos = p[y[te] == 1]; neg = p[y[te] == 0]
    if len(pos) and len(neg):
        wins = sum((pv > nv) for pv in pos for nv in neg) + 0.5 * sum((pv == nv) for pv in pos for nv in neg)
        aucs.append(wins / (len(pos) * len(neg)))
print(f"\n[3] CLASSIFICADOR (regressao logistica, 5-fold CV):")
print(f"  acuracia media: {np.mean(accs)*100:.1f}% (chance={max(y.mean(),1-y.mean())*100:.1f}%)")
print(f"  AUC media: {np.mean(aucs):.3f}")
print(f"  acc folds: {[f'{a*100:.1f}' for a in accs]}")

# top coeficientes
w_full = logreg_fit(Xn, y)
print("\n[4] PESO DE CADA TRACO DO SOTAQUE (coeficientes):")
for f, w in zip(["intercept"] + FEATS, w_full):
    print(f"  {f:26s} {w:+.3f}")

# resumo dos significantes
print("\n[5] RESUMO: features estatisticamente significativas (p<0.05):")
for f, p, dirn in sig:
    print(f"  {f} ({dirn}, p={p:.1e})")

# --- [6] Classificador vs CONTROLE COMUM (o teste mais duro) ---
comuns = []
for l in open(DATA / "dataset_comuns.jsonl"):
    r = json.loads(l)
    if not r.get("sem_tx") and all(f in r for f in FEATS):
        comuns.append(r)
Xc = np.array([[r[f] for f in FEATS] for r in comuns])
X2 = np.vstack([Xs, Xc]); y2 = np.concatenate([np.ones(len(Xs)), np.zeros(len(Xc))])
mu2 = X2.mean(0); sd2 = X2.std(0) + 1e-9
Xn2 = (X2 - mu2) / sd2
Xn2 = np.hstack([np.ones((len(Xn2), 1)), Xn2])
rng2 = np.random.default_rng(42)
idx = rng2.permutation(len(Xn2)); Xn2, y2 = Xn2[idx], y2[idx]
folds2 = np.array_split(np.arange(len(y2)), k)
accs2 = []
for i in range(k):
    te = folds2[i]; tr = np.concatenate([folds2[j] for j in range(k) if j != i])
    w2 = logreg_fit(Xn2[tr], y2[tr])
    pred = (1 / (1 + np.exp(-Xn2[te] @ w2)) >= 0.5).astype(int)
    accs2.append((pred == y2[te]).mean())
print(f"\n[6] CLASSIFICADOR vs CONTROLE COMUM (5-fold CV):")
print(f"  acuracia media: {np.mean(accs2)*100:.1f}% (chance={max(y2.mean(),1-y2.mean())*100:.1f}%)")

json.dump({
    "n_scam": len(scam), "n_honesto": len(hon),
    "vazia_scam_pct": p_scam, "vazia_hon_pct": p_hon, "chi2": chi2,
    "acuracia_cv": float(np.mean(accs)), "auc_cv": float(np.mean(aucs)),
    "significativas": [(f, float(p), d) for f, p, d in sig],
}, open(RESULTS / "resultado_analise.json", "w"), ensure_ascii=False, indent=1)
print("\nSalvo em resultado_analise.json")
