#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fpdf import FPDF

class P(FPDF):
    def footer(self):
        self.set_y(-15); self.set_font("helvetica","I",8)
        self.cell(190,10,f"Independent preprint - ZEUS GUARD Security Lab - page {self.page_no()}",align="C")

p = P(); p.set_auto_page_break(True, 20)
p.add_page()
p.set_font("helvetica","B",16)
p.multi_cell(190,8,"THE DISPOSABLE WALLET")
p.set_font("helvetica","",11)
p.multi_cell(190,6,"Behavioral signatures of cryptocurrency drainer addresses on Ethereum: an empirical study of 1,464 wallets")
p.ln(3)
p.set_font("helvetica","I",9)
p.multi_cell(190,5,"Clebson Campos de Araujo - ZEUS GUARD Security Lab - October 4, 2026\nIndependent research. All data and code included in the deposit.")
p.ln(4)

def h1(t):
    p.ln(2); p.set_font("helvetica","B",13); p.multi_cell(190,7,t); p.ln(1)
def corpo(t):
    p.set_font("helvetica","",10.5); p.multi_cell(190,5.3,t); p.ln(1.5)

h1("ABSTRACT")
corpo("Wallet drainers - malicious contracts and addresses that steal funds through deceptive transaction prompts - are among the most damaging threats in Ethereum, yet they are usually studied after victimization. This work asks a simpler, predictive question: do drainer addresses carry a measurable on-chain behavioral signature before and during their operation? I assembled 1,464 unique Ethereum addresses: 757 confirmed malicious addresses (ScamSniffer incident database), 707 established honest wallets (Etherscan top-activity controls), and 264 recently-active common users (small plain ETH transfers, matched control). FINDING 1 (disposability): 48.5% of malicious addresses are empty or have no transactions at all, versus 9.5% of rich controls and 2.2% of common users (chi-square 266.7, p ~ 6e-60). Drainers are disposable wallets: value flows in and is stripped out through token transfers, leaving an empty, ETH-silent address. FINDING 2 (the accent): among wallets with history, drainers exhibit a distinctive behavioral profile: more unique counterparties (median ~17 vs ~10 rich / ~15 common), a near-dormant rhythm (~1 tx/hour vs ~19 rich / ~39 common), and larger maximum transaction values. All differences survive 2,000-round permutation tests (p < 0.001). FINDING 3 (prediction): a logistic classifier on 8 behavioral features identifies malicious addresses with 70.0% accuracy / AUC 0.784 against rich controls (chance 61.5%) and 74.0% accuracy against matched common controls (chance 59.6%), in 5-fold cross-validation. The signature is robust to control-group choice, cheap to compute (two API calls per address), and directly deployable as a pre-transaction risk signal in wallets and firewalls such as the open-source ZEUS GUARD.")

h1("1. INTRODUCTION")
corpo("Drainer attacks succeed at the moment of signing: the victim approves or sends a transaction that looks legitimate, and funds are pulled by the attacker. Protection today relies mostly on static blocklists and on manually curated labels, which react after attacks are reported. If malicious addresses carry systematic behavioral patterns - an on-chain accent - then those patterns can be scored before the first victim signs, turning post-hoc labeling into pre-transaction defense. This study measures that accent empirically and tests whether it is separable from both elite wallets and ordinary users.")

h1("2. DATA AND METHODS")
corpo("MALICIOUS SET: 757 unique addresses drawn from the ScamSniffer phishing/drainer address database (2,530 raw entries; deduplicated). These are addresses involved in confirmed incident reports. CONTROL RICH: 707 established wallets with public activity collected from Etherscan rankings. CONTROL COMMON (added in the second phase to eliminate the rich-control selection bias): 264 unique EOAs observed sending plain ETH transfers of 0.001-2.0 ETH in recent mainnet blocks - everyday users, sampled by behavior, not by wealth.")
corpo("FEATURES: for each address, the 50 most recent transactions were fetched from the Blockscout v2 API (eth.blockscout.com) and reduced to 8 behavioral features: log10 of the median transaction value, log10 of the maximum value, fraction of transactions sent (vs received), number of unique counterparties, fraction of pure-ETH transfers (empty input data), fraction of reverted transactions, transaction rate per hour, and ETH balance. Two API calls per address; total cost of the entire study: zero (public API).")
corpo("STATISTICS: group differences tested with the Mann-Whitney U rank test and validated with permutation tests (2,000 reshuffles for the rich comparison, 1,000 for the matched comparison) because heavy ties (e.g. zero balances) inflate the normal approximation of U. Categorical comparison (empty wallet yes/no) uses the chi-square test. Classification uses L2-free logistic regression trained by gradient descent, evaluated with stratified 5-fold cross-validation on the full sample, reporting accuracy against the majority-class baseline.")

h1("3. RESULTS")
h1("3.1 Finding 1 - The disposable wallet")
corpo("The single strongest signal is emptiness. 48.5% of malicious addresses hold zero ETH and show no transactions at inspection time, versus 9.5% of rich controls and 2.2% of common users (chi-square 266.7, p ~ 6e-60; n = 1,464). The interpretation is mechanical: a drainer address receives stolen value and immediately forwards it (often as token transfers, which do not require holding ETH), then sits empty waiting for the next victim. Emptiness is not a bug of the dataset - it is the attack pattern itself. A wallet asking for your funds while being provably poor and provably silent is behaving exactly like half of the confirmed attackers in this study.")
h1("3.2 Finding 2 - The accent among active wallets")
corpo("Restricting to addresses with transaction history (389 malicious, 608 rich, 264 common), every behavioral feature separates malicious from honest wallets. Against rich controls: drainers transact with more unique counterparties (mean 17.0 vs 10.3; CLES 0.654), use more pure-ETH transfers (0.54 vs 0.38; CLES 0.637), show larger maximum values (CLES 0.724) and a near-dormant rhythm of ~1.1 tx/hour versus ~19.3 (CLES 0.313). All differences p < 0.001 under permutation. Against MATCHED common users the rhythm signal persists (~1.1 vs ~38.9 tx/hour; CLES 0.297, p = 0.001) and unique counterparties remain elevated (p = 0.029), while the pure-transfer fraction inverts (0.54 vs 0.85) - a selection artifact of the common control (sampled from plain-ETH senders), disclosed for completeness. The core signature - many counterparties, low frequency, disposable balance - is direction-consistent under both controls.")
h1("3.3 Finding 3 - Prediction before the label")
corpo("A logistic classifier on the 8 features identifies malicious wallets with 70.0% mean accuracy across 5 folds against rich controls (majority baseline 61.5%; AUC 0.784) and 74.0% against matched common controls (baseline 59.6%). Feature weights confirm the profile: transaction rate is the dominant negative predictor (w = -1.98), followed by balance (w = -0.96) and fraction sent (w = -0.81); unique counterparties (+0.64) and maximum value (+0.59) push toward malicious. The classifier sees only ordinary public behavior - no labels, no blocklists - and still recovers most of the attacker population.")

h1("4. LIMITATIONS (DISCLOSED IN FULL)")
corpo("(1) Labels come from one source (ScamSniffer) and encode what that vendor detects, biased toward high-value incidents. (2) The rich control is active and wealthy by construction; the common control is biased toward plain-ETH senders by its sampling rule. Both biases are disclosed and the two controls bracket the honest population. (3) The 50-transaction window may mix pre-attack and post-attack behavior. (4) AUC 0.784 is far from forensic-grade precision; false positives would harm honest users, so this signal should gate risky actions softly (warnings, limits) rather than hard-block, as ZEUS GUARD does with its daily cap. (5) Sophisticated actors can mimic honest patterns once this study is public - the arms race is real; the disposability signal, however, is costly to fake, since operating with a funded, active, history-rich wallet raises the attacker's costs.")

h1("5. ETHICS")
corpo("This is defensive research. All addresses analyzed are public (blockchain) or published by security vendors in incident reports. No private data, no de-anonymization, no attack tooling is included. The intended use is risk-scoring interfaces that PROTECT users - the motivation is the open-source pre-transaction firewall ZEUS GUARD (github.com/clebson-scott/zeus-guard).")

h1("6. REPRODUCIBILITY")
corpo("The deposit includes: dataset.jsonl, dataset2.jsonl, dataset3.jsonl, dataset_comuns.jsonl (raw per-address features), coleta.py, coleta2.py, conserta.py, controle_comum.py (collectors), analise.py, permutacao.json, resultado_analise.json (analysis), figura.py and the figure. Any researcher with network access can reproduce every number with zero cost.")

p.ln(3)
p.set_font("helvetica","B",12); p.multi_cell(190,7,"FIGURE 1 - The on-chain accent of drainers"); p.ln(1)
p.image("figura_sotaque_drainer.png", x=10, w=190)
p.set_font("helvetica","",9); p.ln(2)
p.multi_cell(190,5,"Behavioral distributions of malicious addresses (red), rich honest controls (blue) and matched common users (green). A: fraction of empty/no-transaction addresses. B-F: feature distributions over the last 50 transactions per wallet.")

p.output("paper_drainer.pdf")
print("paper_drainer.pdf gerado")
