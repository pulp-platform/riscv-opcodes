# Unratified and custom extensions

Custom (vendor) extensions live in this directory; see `PULP.md` at the
repository root for how to add one.

## Snitch / Spatz notes

The Snitch cluster and the Spatz (Snitch + vector unit) cluster are separate
hardware projects that both generate their decoder packages and `encoding.h`
from this repository, each with its own extension selection (see
`util/clustergen/opcodes.txt` in `snitch_cluster`, and the `OPCODES` list in
the Spatz repository Makefile). Points to keep in mind when touching the
shared files:

- `flb`/`fsb` in `rv_xsmallfloat_b` use funct3=4, matching the Spatz
  implementation (decided with the maintainers): funct3=0 at
  LOAD-FP/STORE-FP is the `vle8.v`/`vse8.v` space and cannot coexist with
  the V extension in one decoder. *Consumers that implemented the former
  funct3=0 encoding must regenerate decoder and toolchain together.*
