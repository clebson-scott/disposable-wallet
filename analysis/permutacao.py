#!/usr/bin/env python3
"""Verificador de reprodutibilidade das estatisticas do 'sotaque on-chain'.

Recomputa, a partir dos datasets brutos (data/dataset*.jsonl):
  - medias por grupo (d_scam / d_hon / d_comum)
  - CLES (Common Language Effect Size) via ranks de Mann-Whitney
e compara cada valor contra os resultados publicados em
analysis/results/permutacao.json e permutacao_comum.json (tolerancia 1e-9).

Em seguida, roda os testes de permutacao com seed fixa (2000 perm. para
scam vs honestos; 1000 perm. para scam vs comuns) e grava
analysis/results/permutacao_reproducao.json / permutacao_comum_reproducao.json.

NOTA HONESTA (Lei da verdade): as medias e os CLES publicados reproduzem
AO ULTIMO DIGITO (tolerancia 1e-9) - verificado por este script e pela CI.
Os p-valores de permutacao do 'sotaque' (log_mediana, log_max,
frac_enviadas, contrapartes_unicas, frac_transferencia_pura, tx_por_hora
vs honestos) reproduzem o piso 1/(N+1), identico ao publicado. P-valores de
sinais FRACOS podem divergir do publicado (ex.: balance_eth scam-vs-honestos
0.0390 -> 0.0005 aqui, consistente com o CLES 0.365 a ~7 sigma), porque o
script original da publicacao era ad-hoc e nao foi arquivado; este modulo e
a implementacao de referencia com seed fixa. Os arquivos publicados
permanecem como artefato historico citado no preprint (DOI
10.5281/zenodo.23136779); divergencias documentadas em docs/METHODOLOGY.md.
"""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "analysis" / "results"

FEATS = ["log_mediana", "log_max", "frac_enviadas", "contrapartes_unicas",
         "frac_transferencia_pura", "frac_revert", "tx_por_hora", "balance_eth"]
# o arquivo publicado scam-vs-honestos traz 7 features (sem frac_revert);
# o scam-vs-comuns traz as 8
FEATS_HON = [f for f in FEATS if f != "frac_revert"]

def carrega(labs):
    regs = {}
    for arq in ["dataset.jsonl", "dataset2.jsonl", "dataset3.jsonl"]:
        for l in open(DATA / arq):
            r = json.loads(l)
            if r["label"] in labs:
                regs[r["addr"]] = r
    return [r for r in regs.values() if not r.get("sem_tx") and all(f in r for f in FEATS)]

def cles(x, y):
    """P(x > y) + 0.5*P(x == y) via ranks de Mann-Whitney U (O(n log n))."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    nx, ny = len(x), len(y)
    allv = np.concatenate([x, y])
    order = np.argsort(allv, kind="mergesort")
    ranks = np.empty(len(allv), float)
    sv = allv[order]
    i = 0
    while i < len(sv):
        j = i
        while j < len(sv) and sv[j] == sv[i]:
            j += 1
        ranks[order[i:j]] = (i + j + 1) / 2.0
        i = j
    U = ranks[:nx].sum() - nx * (nx + 1) / 2.0
    return U / (nx * ny)

def p_perm(xs, ys, n_perm, rng):
    """Permuta labels n_perm vezes; p one-sided na direcao observada."""
    a, b = np.asarray(xs, float), np.asarray(ys, float)
    obs = cles(a, b)
    comb = np.concatenate([a, b])
    na = len(a)
    count = 0
    for _ in range(n_perm):
        rng.shuffle(comb)
        c = cles(comb[:na], comb[na:])
        if (c >= obs) if obs >= 0.5 else (c <= obs):
            count += 1
    return obs, (count + 1) / (n_perm + 1)

def main():
    scam = carrega(["scam"])
    hon = carrega(["honesto"])
    comuns = [r for r in (json.loads(l) for l in open(DATA / "dataset_comuns.jsonl"))
              if not r.get("sem_tx") and all(f in r for f in FEATS)]
    print(f"com historico: scam {len(scam)} | honesto {len(hon)} | comum {len(comuns)}")

    pub = json.load(open(RESULTS / "permutacao.json"))
    pubc = json.load(open(RESULTS / "permutacao_comum.json"))

    ok = True
    repro = {}
    repro_c = {}
    print("\n[1] SCAM vs HONESTOS - reproducao dos publicados (tol 1e-9):")
    for f in FEATS_HON:
        xs = [r[f] for r in scam]; ys = [r[f] for r in hon]
        m_s, m_h = float(np.mean(xs)), float(np.mean(ys))
        c = cles(xs, ys)
        ref = pub[f]
        ok_f = (abs(m_s - ref["d_scam"]) < 1e-9 and abs(m_h - ref["d_hon"]) < 1e-9
                and abs(c - ref["cles"]) < 1e-12)
        ok &= ok_f
        print(f"  {f:26s} mean_scam={m_s:>10.4f} mean_hon={m_h:>10.4f} cles={c:.4f}  {'PASS' if ok_f else 'FAIL'}")
        repro[f] = {"d_scam": m_s, "d_hon": m_h, "cles": c}
    print("\n[2] SCAM vs COMUNS - reproducao dos publicados (tol 1e-9):")
    for f in FEATS:
        xs = [r[f] for r in scam]; yc = [r[f] for r in comuns]
        m_s, m_c = float(np.mean(xs)), float(np.mean(yc))
        c = cles(xs, yc)
        ref = pubc[f]
        ok_f = (abs(m_s - ref["scam"]) < 1e-9 and abs(m_c - ref["comum"]) < 1e-9
                and abs(c - ref["cles"]) < 1e-12)
        ok &= ok_f
        print(f"  {f:26s} mean_scam={m_s:>10.4f} mean_comum={m_c:>10.4f} cles={c:.4f}  {'PASS' if ok_f else 'FAIL'}")
        repro_c[f] = {"scam": m_s, "comum": m_c, "cles": c}

    print("\n[3] PERMUTACOES (seed fixa 42/43):")
    rng = np.random.default_rng(42)
    for f in FEATS_HON:
        c, p = p_perm([r[f] for r in scam], [r[f] for r in hon], 2000, rng)
        repro[f]["p_perm"] = p
        repro[f]["p_publicado"] = pub[f]["p_perm"]
        print(f"  {f:26s} p_reproduzido={p:.4f} p_publicado={pub[f]['p_perm']:.4f}")
    rng = np.random.default_rng(43)
    for f in FEATS:
        c, p = p_perm([r[f] for r in scam], [r[f] for r in comuns], 1000, rng)
        repro_c[f]["p"] = p
        repro_c[f]["p_publicado"] = pubc[f]["p"]
        print(f"  [comum] {f:20s} p_reproduzido={p:.4f} p_publicado={pubc[f]['p']:.4f}")

    json.dump(repro, open(RESULTS / "permutacao_reproducao.json", "w"), indent=1)
    json.dump(repro_c, open(RESULTS / "permutacao_comum_reproducao.json", "w"), indent=1)
    print("\nSalvo: permutacao_reproducao.json / permutacao_comum_reproducao.json")
    print("VERIFICACAO DAS ESTATISTICAS PUBLICADAS:", "PASS" if ok else "FAIL")
    if not ok:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
