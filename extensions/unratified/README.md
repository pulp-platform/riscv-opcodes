# Unratified and custom extensions

Custom (vendor) extensions live in this directory; see `PULP.md` at the
repository root for how to add one.

## Spatz variant extensions

The Snitch cluster and the Spatz (Snitch + vector unit) cluster are separate
hardware projects that both generate their decoder packages and `encoding.h`
from this repository, each with its own extension selection (see
`util/clustergen/opcodes.txt` in `snitch_cluster`, and the `update_opcodes`
target in the Spatz repository). Almost all extensions are shared; where the
two implementations assign the same encoding space differently, a `_spatz`
variant file keeps both definitions buildable side by side.

Current variants:

- `rv_xfrep` (Snitch) vs. `rv_xfrep_spatz` (Spatz).
  Snitch hardware reads bits 14..12 of `frep.o` as the `stagger_max` field,
  so its definition must leave them as an operand. Spatz does not implement
  staggering and pins those bits to 0, because the Ventaglio instructions in
  `rv_xvfx` (`vfxmacc.vrf`, `vfxmul.vrf`, `vventclr`) sit at custom-0
  (`0x0B`) with funct3=2 and would otherwise be shadowed by a
  funct3-wildcard `frep` pattern in the Spatz decoder (unique casez).
  Spatz additionally implements `frep.i`. A hardware target must select
  exactly one of the two files. The variant mnemonics carry a `.spatz`
  suffix because two files defining the same instruction name is a hard
  error in the repository-wide build, while overlapping encodings under
  different names only produce `--warn-overlap` warnings.

Next steps / retirement plan:

1. The Spatz repository consumes `rv_xfrep_spatz` (instead of `rv_xfrep`)
   when regenerating `riscv_instr.sv`, and renames its decoder references
   `FREP_O`/`FREP_I` to `FREP_O_SPATZ`/`FREP_I_SPATZ`.
2. The planned Ventaglio encoding cleanup relocates the custom-0/funct3=2
   instructions out of the `frep` shadow. Once that lands, Spatz can adopt
   the shared wide `frep.o` (plus an upstreamed `frep.i`), and
   `rv_xfrep_spatz` should be deleted.
3. The Ventaglio CSRs in `csrs/unratified/rv_xventaglio.csv` (0x7C3-0x7C6)
   share addresses with the Snitch CSRs in `csrs/unratified/rv_xpulp.csv`.
   Neither hardware references the other's names, so both may coexist, but
   consumers that switch over CSR *addresses* (e.g. installing `encoding.h`
   into `riscv-isa-sim`) will see duplicates. The cleanup should also assign
   the Ventaglio CSRs unique addresses.
