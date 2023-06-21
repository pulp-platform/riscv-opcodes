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

  For example the outputs of `parse-opcodes` can be used in other parts of a project like
  assembler, ISA simulator, riscv-tests, apps runtime or RTL decoder.

- opcodes description files organization matches the same of the official
  repository upstream [riscv-opcodes](https://github.com/riscv/riscv-opcodes),
  with the addition of several custom instruction set extensions: you can
  add your own custom extensions as text file in the root, then create a configuration in
  `config.mk` and subsequently add that variable to the variable `MY_OPCODES` of the `Makefile`
- in the `Makefile`, you can select which opcodes files not to take into account
  for the parsing script execution, basing on the target architecture, by
  listing them in the variable `DISCARDED_OPCODES`;
- opcodes files from the official 128-bit extension have not been introduced
  due to the other changes which they imply to other opcodes specifications;
- some of the instructions originally declared in the vectorial extension
  (`opcodes-rvv` file) have been set as pseudo-instruction due to the overlapping
  of their opcodes space with the opcodes space of the SIMD instructions from
  Xpulpv2, defined in `opcodes-xpulpvect_CUSTOM` and `opcodes-xpulpvectshufflepack_CUSTOM`.


## Smallfloat notice

The Snitch cores use `opcodes-flt-occamy` to decode smallfloat instructions.
`opcodes-sflt` is not used but describes how ariane (CVA6) decodes
instructions. This file is not used but kept in this repository for reference.
Ariane and Snitch do not use the same FPU configuration.


## Overlap notices
There might be some overlap in opcodes between extensions. These are noted as far as known
in the corresponding files. In some cases these overlaps can be avoided by making one of the
opcodes a pseudo-opcodes using `@` in front.

## Control and Status Registers

### HW-Loop Register Collisions

There are three existing address spaces for the HW-Loop [CSRs defined in binutils](https://iis-git.ee.ethz.ch/gnu/riscv-binutils-gdb/-/blob/riscv-binutils-2.34-pulp/include/opcode/riscv-opc.h#L829), all of them have collisions.
The default configuration uses the CV32E40P addresses.

#### CV32E40P

The addresses 0x800-0x802 and 0x804-0x806 are used, this collides with the fmode CSR used in Snitch.
The source of the HW-Loop addresses: https://cv32e40p.readthedocs.io/en/latest/control_status_registers/
The [offending riscv-opcodes commit](https://github.com/pulp-platform/riscv-opcodes/commit/1e5fa7787b4e388c51956f6e7fd26d4d249a7d80) that adds the collisions from Snitch: (file parse_opcodes, line 124)

#### PULPv3

The addresses 0x7C0 - 0x7C2 and 0x7C4-0x7C6 are used, this collides with the ssr and fpmode CSRs used in Snitch.
The [offending riscv-opcodes commit](https://github.com/pulp-platform/riscv-opcodes/commit/1e5fa7787b4e388c51956f6e7fd26d4d249a7d80) that adds the collisions from Snitch: (file parse_opcodes, line 133-134)

#### PULPv1

The addresses 0x7B0 - 0x7B2 and 0x7B4-0x7B6 are used, this collides with the debug mode registers (dcsr, dpc, dscratch0) from the official spec (page 11 in [RISCV priviliged v1.12](https://github.com/riscv/riscv-isa-manual/releases/download/Priv-v1.12/riscv-privileged-20211203.pdf)).
There is no reason to use this for anything new, it is considered DEPRECATED.

