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
variant file keeps both definitions buildable side by side. Variant
mnemonics carry a `.spatz` suffix because two files defining the same
instruction name is a hard error in the repository-wide build, while
overlapping encodings under different names only produce `--warn-overlap`
warnings.

Current variants:

- `rv_xsmallfloat_b` (Snitch/Occamy `flb`/`fsb` at funct3=0) vs.
  `rv_xsmallfloat_spatz` (`flb.spatz`/`fsb.spatz` at funct3=4).
  Spatz hardware implements the pre-Occamy draft encoding: funct3=0 at
  LOAD-FP overlaps the `vle8.v` space in the Spatz decoder (unique casez),
  and the post-increment loads (`p.flb.rrpost` in `rv_xrrpost`) are
  internally re-encoded to a funct3=4 `flb` on the Spatz accelerator
  interface. This variant is selected *in addition to* `rv_xsmallfloat_b`
  (only the two load/store encodings differ; the Spatz decoder simply
  references `FLB_SPATZ`/`FSB_SPATZ` instead of `FLB`/`FSB`).

Related notes:

- Spatz does not implement `frep`; it selects neither `rv_xfrep` nor any
  variant of it. The Ventaglio instructions in `rv_xvfx` overlap the
  (Snitch-only) `frep.o` encoding at custom-0, which is fine as the two
  are never decoded by the same core.

Next steps / retirement plan:

1. The planned Ventaglio encoding cleanup should decide whether Spatz
   migrates `flb`/`fsb` to the Occamy funct3=0 encoding (this requires
   changing the internal re-encoding of the `p.fl*.rrpost` path and
   resolving the `vle8.v` decode ambiguity in the Spatz core), after which
   `rv_xsmallfloat_spatz` can be deleted.
2. The Ventaglio CSRs in `csrs/unratified/rv_xventaglio.csv` (0x7C3-0x7C6)
   share addresses with the Snitch CSRs in `csrs/unratified/rv_xpulp.csv`.
   Neither hardware references the other's names, so both may coexist, but
   consumers that switch over CSR *addresses* (e.g. installing `encoding.h`
   into `riscv-isa-sim`) will see duplicates. The cleanup should also assign
   the Ventaglio CSRs unique addresses.
