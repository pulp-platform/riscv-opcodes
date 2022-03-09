riscv-opcodes
===========================================================================

This repo enumerates standard RISC-V instruction opcodes and control and
status registers, as well as some custom modifications.  It also contains a
script to convert them into several formats (C, Python, Go, SystemVerilog, Scala, LaTeX),
starting from their high-level, human-readable description.

## Practical info
- Every output of the parser is generated inside this folder; tools which
  need such automatically generated files must use soft link to point to them.
  For example, supposing `RISCV_ISA_SIM_TOOL` is set to the source code directory of
  the Spike simulator:

  ```bash
  ln -sfr encoding_out.h $RISCV_ISA_SIM_TOOL/encoding.h
  ```

  Example of where the outputs of `parse-opcodes` are used in other projects

  | Parser output  | Destination                                    |
  |:--------------:|:-----------------------------------------------|
  | encoding_out.h | riscv-gnu-toolchain/riscv-binutils-gdb/include/opcode/riscv-opc.h <br> riscv-isa-sim/riscv/encoding.h <br> riscv-pk/machine/encoding.h <br> riscv-tests/env/encoding.h <br> riscv-openocd/src/target/riscv/encoding.h <br> _custom use_ i.e. apps/common/encoding.h |
  | inst.sverilog  | snitch/src/riscv_instr.sv |

- opcodes description files organization matches the same of the official
  repository upstream [riscv-opcodes](https://github.com/riscv/riscv-opcodes),
  with the addition of several custom instruction set extensions: you can
  add your own custom extensions as text file in the root, subsequently
  adding it to the variable `MY_OPCODES` of the `Makefile`
- in the `Makefile`, you can select which opcodes files not to take into account
  for the parsing script execution, basing on the target architecture, by
  listing them in the variable `DISCARDED_OPCODES`;
- opcodes files from the official 128-bit extension have not been introduced
  due to the other changes which they imply to other opcodes specifications;
- some of the instructions originally declared in the vectorial extension
  (`opcodes-rvv` file) have been set as pseudo-instruction due to the overlapping
  of their opcodes space with the opcodes space of the SIMD instructions from
  Xpulpv2, defined in `opcodes-xpulpimg_CUSTOM`.


## Smallfloat notice

The Snitch cores use `opcodes-flt-occamy` to decode smallfloat instructions.
`opcodes-sflt` is not used but describes how ariane (CVA6) decodes 
instructions. This file is not used but kept in this repository for reference.
Ariane and Snitch do not use the same FPU configuration.


## Snitch notices
`opcodes-sflt = opcodes-sflt_CUSTOM opcodes-rv32d-zfh_DRAFT opcodes-rv32q-zfh_DRAFT opcodes-rv32zfh_DRAFT opcodes-rv64zfh_DRAFT`
for instructions `flb, fsb, fcvt.h.b, fcvt.b.h` an `@` is now used in front

`opcodes-flt-occamy` will conflict with `opcodes-sflt_CUSTOM`, `opcodes-rv32d-zfh_DRAFT`, `opcodes-rv32q-zfh_DRAFT`, `opcodes-rv32zfh_DRAFT`, `opcodes-rv64zfh_DRAFT`

`hfence.bvma` was renamed to `hfence.vvma` (same opcode)

the RV32B opcodes were put into its own custom file `opcodes-rv32b_CUSTOM`

## Overlap notices
`opcodes-rvv` and `opcodes-xpulpbitop_CUSTOM` overlap

`opcodes-xpulpbitop_CUSTOM` is superset of `opcodes-xpulpbitopsmall_CUSTOM`

`opcodes-flt-occamy_CUSTOM` overlaps `opcodes-sflt_CUSTOM`, `opcodes-rv32d-zfh_DRAFT`, `opcodes-rv32q-zfh_DRAFT`, `opcodes-rv32zfh_DRAFT`, `opcodes-rv64zfh_DRAFT`

`opcodes-rv32b_CUSTOM` overlaps `opcodes-xpulpbitop_CUSTOM`,`opcodes-xpulpbitopsmall_CUSTOM`

`opcodes-xpulphwloop_CUSTOM` overlaps `opcodes-ipu_CUSTOM`

`opcodes-xpulpminmax_CUSTOM` overlaps `opcodes-rv32b_CUSTOM`