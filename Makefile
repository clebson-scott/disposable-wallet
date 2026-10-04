# The Disposable Wallet — make analysis | verify | figure | paper | all | collect
.PHONY: all analysis verify figure paper collect

all: analysis verify figure paper

analysis:
	python3 analysis/analise.py

verify:
	python3 analysis/permutacao.py

figure:
	python3 figures/figura.py

paper: figure
	python3 paper/paper_drainer.py

collect:
	python3 collection/coleta.py
	python3 collection/coleta2.py
	python3 collection/coleta3.py
	python3 collection/conserta.py
	python3 collection/controle_comum.py
