#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coleta de features on-chain: 400 scam (ScamSniffer) vs 400 honestos (mainnet aleatoria)"""
import json, urllib.request, time, random, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

BS = "https://eth.blockscout.com/api/v2"
def get(url, tries=4):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64)"})
            return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception as e:
            time.sleep(1.5 * (t+1))
    return None

def coleta(addr, label):
    r = {"addr": addr, "label": label}
    info = get(f"{BS}/addresses/{addr}")
    if not info: return None
    r["is_contract"] = info.get("is_contract", False)
    r["balance_eth"] = (int(info.get("coin_balance") or 0)) / 1e18
    r["has_ens"] = bool(info.get("ens_domain_name"))
    r["bs_scam_flag"] = bool(info.get("is_scam"))
    c = get(f"{BS}/addresses/{addr}/counters")
    if not c: return None
    r["tx_count"] = int(c.get("transactions_count") or 0)
    r["token_transfers"] = int(c.get("token_transfers_count") or 0)
    r["gas_usage"] = int(c.get("gas_usage_count") or 0)
    if r["tx_count"] == 0 or r["is_contract"]:
        r["sem_tx"] = r.get("tx_count", 0) == 0
        return r
    tx = get(f"{BS}/addresses/{addr}/transactions")
    if not tx or not tx.get("items"):
        r["sem_tx"] = True
        return r
    items = tx["items"][:50]
    vals = [int(t.get("value") or 0)/1e18 for t in items]
    otherside = []
    n_from = 0; plain = 0; revert = 0
    for t in items:
        f = (t.get("from") or {}).get("hash","").lower()
        to = (t.get("to") or {}).get("hash","").lower() if t.get("to") else ""
        if f == addr: n_from += 1
        other = to if f == addr else f
        if other: otherside.append(other)
        if (t.get("raw_input") or "0x") == "0x": plain += 1
        if t.get("result") not in ("success", None): revert += 1
    times = [t.get("timestamp") for t in items if t.get("timestamp")]
    span_h = (max(times) - min(times))/3600 if len(times) > 1 else 0
    r["n_tx"] = len(items)
    r["mediana_valor"] = sorted(vals)[len(vals)//2] if vals else 0
    r["max_valor"] = max(vals) if vals else 0
    r["log_mediana"] = r["mediana_valor"] and max(-20, 0)  # placeholder substituido abaixo
    import math
    r["log_mediana"] = math.log10(r["mediana_valor"]) if r["mediana_valor"] > 0 else -20
    r["log_max"] = math.log10(r["max_valor"]) if r["max_valor"] > 0 else -20
    r["frac_enviadas"] = n_from / len(items)
    r["contrapartes_unicas"] = len(set(otherside))
    r["frac_transferencia_pura"] = plain / len(items)
    r["frac_revert"] = revert / len(items)
    r["tx_por_hora"] = len(items)/span_h if span_h > 0 else 0
    r["sem_tx"] = False
    return r

scam = json.load(open("scam_addrs.json"))
ctrl = json.load(open("control_candidates.json"))
random.Random(42).shuffle(scam); random.Random(43).shuffle(ctrl)
alvos = [(a, "scam") for a in scam[:450]] + [(a, "honesto") for a in ctrl[:450]]

out = open("dataset.jsonl", "w")
lock = threading.Lock(); feitos = [0]
def job(a, l):
    r = coleta(a, l)
    with lock:
        feitos[0] += 1
        if feitos[0] % 50 == 0: print(f"progresso: {feitos[0]}/{len(alvos)}", flush=True)
        if r: out.write(json.dumps(r)+"\n"); out.flush()
    return None

with ThreadPoolExecutor(max_workers=6) as ex:
    for a, l in alvos:
        ex.submit(job, a, l)
out.close()
print("FIM - dataset.jsonl:", sum(1 for _ in open("dataset.jsonl")), "registros")
