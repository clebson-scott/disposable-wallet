#!/usr/bin/env python3
"""Refetch: para registros marcados sem_tx, busca transacoes direto (counters mentia)"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED = DATA / "seed"
RESULTS = ROOT / "analysis" / "results"
FIGURES = ROOT / "figures"
PAPERS = ROOT / "paper"

import json, urllib.request, time, math, threading
from concurrent.futures import ThreadPoolExecutor
BS = "https://eth.blockscout.com/api/v2"
def get(url, tries=3):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception:
            time.sleep(1+t)
    return None

rows = [json.loads(l) for l in open(DATA / "dataset.jsonl")]
pend = [r for r in rows if r.get("sem_tx")]
lock = threading.Lock(); print("refetch:", len(pend), flush=True)

def txfeats(r):
    tx = get(f"{BS}/addresses/{r['addr']}/transactions")
    if not tx or not tx.get("items"): return
    items = tx["items"][:50]
    vals = [int(t.get("value") or 0)/1e18 for t in items]
    n_from = 0; plain = 0; revert = 0; other_set = set()
    for t in items:
        f = (t.get("from") or {}).get("hash","").lower()
        to = (t.get("to") or {}).get("hash","").lower() if t.get("to") else ""
        if f == r["addr"]: n_from += 1
        o = to if f == r["addr"] else f
        if o: other_set.add(o)
        if (t.get("raw_input") or "0x") == "0x": plain += 1
        if t.get("result") not in ("success", None): revert += 1
    ts = [t.get("timestamp") for t in items if t.get("timestamp")]
    times = [t.replace("T"," ").replace("Z","") for t in ts]
    from datetime import datetime
    dt = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f") if "." in t else datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in times]
    span_h = (max(dt)-min(dt)).total_seconds()/3600 if len(dt) > 1 else 0
    med = sorted(vals)[len(vals)//2]; mx = max(vals)
    r.update({
        "n_tx": len(items), "mediana_valor": med, "max_valor": mx,
        "log_mediana": math.log10(med) if med > 0 else -20,
        "log_max": math.log10(mx) if mx > 0 else -20,
        "frac_enviadas": n_from/len(items),
        "contrapartes_unicas": len(other_set),
        "frac_transferencia_pura": plain/len(items),
        "frac_revert": revert/len(items),
        "tx_por_hora": len(items)/span_h if span_h > 0 else 0,
        "sem_tx": False})

with ThreadPoolExecutor(max_workers=6) as ex:
    futs = [ex.submit(txfeats, r) for r in pend]
    for i, f in enumerate(futs):
        f.result()
        if (i+1) % 60 == 0: print("progresso refetch:", i+1, flush=True)

with open(DATA / "dataset.jsonl","w") as out:
    for r in rows: out.write(json.dumps(r)+"\n")
from collections import Counter
print("FIM. agora com tx:", Counter((r['label'], r.get('sem_tx', True)) for r in rows))
