#!/usr/bin/env python3
"""Lote 3: fechar 400 scam + 400 honesto com a logica corrigida (transactions direto)."""
import json, urllib.request, time, math, threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
BS = "https://eth.blockscout.com/api/v2"

def get(url, tries=3):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception:
            time.sleep(1 + t)
    return None

def parse_t(t):
    t = t.replace("T", " ").replace("Z", "")
    return datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f" if "." in t else "%Y-%m-%d %H:%M:%S")

def coleta(addr, label):
    r = {"addr": addr, "label": label}
    info = get(f"{BS}/addresses/{addr}")
    if not info: return None
    r["is_contract"] = bool(info.get("is_contract"))
    r["balance_eth"] = int(info.get("coin_balance") or 0) / 1e18
    r["has_ens"] = bool(info.get("ens_domain_name"))
    r["bs_scam_flag"] = bool(info.get("is_scam"))
    tx = get(f"{BS}/addresses/{addr}/transactions")
    if not tx or not tx.get("items"):
        r["sem_tx"] = True
        return r
    items = tx["items"][:50]
    vals = [int(t.get("value") or 0) / 1e18 for t in items]
    n_from = 0; plain = 0; revert = 0; other_set = set()
    for t in items:
        f = (t.get("from") or {}).get("hash", "").lower()
        to = (t.get("to") or {}).get("hash", "").lower() if t.get("to") else ""
        if f == addr: n_from += 1
        o = to if f == addr else f
        if o: other_set.add(o)
        if (t.get("raw_input") or "0x") == "0x": plain += 1
        if t.get("result") not in ("success", None): revert += 1
    ts = [parse_t(t["timestamp"]) for t in items if t.get("timestamp")]
    span_h = (max(ts) - min(ts)).total_seconds() / 3600 if len(ts) > 1 else 0
    med = sorted(vals)[len(vals) // 2]; mx = max(vals)
    r.update({"n_tx": len(items), "mediana_valor": med, "max_valor": mx,
              "log_mediana": math.log10(med) if med > 0 else -20,
              "log_max": math.log10(mx) if mx > 0 else -20,
              "frac_enviadas": n_from / len(items),
              "contrapartes_unicas": len(other_set),
              "frac_transferencia_pura": plain / len(items),
              "frac_revert": revert / len(items),
              "tx_por_hora": len(items) / span_h if span_h > 0 else 0,
              "sem_tx": False})
    return r

scam = json.load(open("scam_addrs.json"))
ctrl = json.load(open("control_candidates.json"))
ja = set()
for arq in ["dataset.jsonl", "dataset2.jsonl", "dataset3.jsonl"]:
    for l in open(arq):
        ja.add(json.loads(l)["addr"])

scam_faltam = [a for a in scam if a not in ja]
ctrl_faltam = [a for a in ctrl if a not in ja]
alvos = [(a, "scam") for a in scam_faltam[:150]] + [(a, "honesto") for a in ctrl_faltam[:420]]
print("alvos lote 3:", len(alvos), "| scam:", min(150, len(scam_faltam)), "| honesto:", min(420, len(ctrl_faltam)), flush=True)

out = open("dataset3.jsonl", "a")
lock = threading.Lock(); n = [0]

def job(a, l):
    r = coleta(a, l)
    with lock:
        n[0] += 1
        if n[0] % 60 == 0: print("progresso:", n[0], flush=True)
        if r:
            out.write(json.dumps(r) + "\n"); out.flush()

with ThreadPoolExecutor(max_workers=6) as ex:
    for a, l in alvos:
        ex.submit(job, a, l)
out.close()
print("FIM lote 3")
