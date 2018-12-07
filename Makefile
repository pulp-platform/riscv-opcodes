SHELL := /bin/sh

ALL_OPCODES := opcodes-pseudo opcodes opcodes-rvc opcodes-rvc-pseudo opcodes-custom


inst.chisel: $(ALL_OPCODES) parse-opcodes
	cat opcodes opcodes-rvc opcodes-rvc-pseudo opcodes-custom opcodes-pseudo | ./parse-opcodes -chisel > $@

inst.go: opcodes opcodes-pseudo parse-opcodes
	cat opcodes opcodes-pseudo opcodes-pulp | ./parse-opcodes -go > $@

inst.c: opcodes opcodes-pseudo parse-opcodes
	cat opcodes opcodes-pseudo opcodes-pulp | ./parse-opcodes -c > $@

inst.sv: opcodes opcodes-pseudo parse-opcodes
	cat opcodes opcodes-rvc opcodes-rvc-pseudo opcodes-pseudo opcodes-pulp | ./parse-opcodes -sv > $@

inst.py: opcodes opcodes-pseudo parse-opcodes
	cat opcodes opcodes-pseudo opcodes-pulp | ./parse-opcodes -py > $@


instr-table.tex: $(ALL_OPCODES) parse-opcodes
	cat opcodes opcodes-pseudo opcodes-pulp | ./parse-opcodes -tex > $@

priv-instr-table.tex: $(ALL_OPCODES) parse-opcodes
	cat opcodes opcodes-pseudo | ./parse-opcodes -privtex > $@
