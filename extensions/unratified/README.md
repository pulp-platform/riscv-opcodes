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
  the V extension in one decoder. Consumers that implemented the former
  funct3=0 encoding must regenerate decoder and toolchain together.
- Spatz does not implement `frep` and does not select `rv_xfrep`. The
  Ventaglio instructions in `rv_xvfx` overlap the (Snitch-only) `frep.o`
  encoding at custom-0, which is fine as the two are never decoded by the
  same core.
- If the two implementations ever assign the same encoding space
  differently again, add a variant file whose mnemonics carry a suffix
  (e.g. `.spatz`): two files defining the same instruction name is a hard
  error in the repository-wide build, while overlapping encodings under
  different names only produce `--warn-overlap` warnings. Each hardware
  target then selects exactly one of the variants.

Open items for the planned Ventaglio encoding cleanup:

1. The Ventaglio CSRs in `csrs/unratified/rv_xventaglio.csv` (0x7C3-0x7C6)
   share addresses with the Snitch CSRs in `csrs/unratified/rv_xpulp.csv`.
   Neither hardware references the other's names, so both may coexist, but
   consumers that switch over CSR *addresses* (e.g. installing `encoding.h`
   into `riscv-isa-sim`) will see duplicates. The cleanup should assign
   the Ventaglio CSRs unique addresses.
