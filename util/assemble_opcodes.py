#!/usr/env python3
# Copyright 2023 ETH Zurich and University of Bologna.
# Solderpad Hardware License, Version 0.51, see LICENSE for details.
# SPDX-License-Identifier: SHL-0.51

# Authors:
# - Thomas Benz <tbenz@iis.ee.ethz.ch>

"""Assemble RISC-V opcodes from ISA string"""
import argparse
import json
import glob
import sys


def ext_op_files(exts: list, files: list, bit_width: int, ops: dict):
    """Translates and resolves extension dependencies in opcode files"""
    for ext in exts:
        found = False
        for bit_ext in [f'rv_{ext}', f'rv{bit_width}_{ext}']:
            if bit_ext in ops:
                found = True
                if ops[bit_ext]['file'] != '':
                    files.append(ops[bit_ext]['file'])
                # dependencies?
                if ops[bit_ext]['dep']:
                    ext_op_files(ops[bit_ext]['dep'], files, bit_width, ops)

        # unknown extension
        if not found:
            print(f'{ext} not found', file=sys.stderr)
            sys.exit(-1)


def read_all_ops(directory: str) -> dict:
    """Read in all opcodes"""
    all_ops = [i[1+len(directory):].split('_') for i in sorted(glob.glob(f'{directory}/*'))]

    ops = {}
    for op in all_ops:
        # extension_name
        name = f'{op[0]}_{op[-1]}'
        # dependencies
        if len(op) > 2:
            dependencies = op[1:-1]
        else:
            dependencies = []
        # assemble
        ops[name] = {'file': '_'.join(op), 'dep': dependencies}
    return ops


def add_dependencies(ops: list, cfg_file: str) -> list:
    with open(cfg_file, encoding='utf-8') as json_content:
        extra_deps = json.load(json_content)

    for extra_dep in extra_deps:
        dep = extra_dep.lower()
        pos_vars = ['rv_', 'rv32_', 'rv64_', 'rv128_']
        for var in pos_vars:
            if f'{var}{dep}' in ops:
                for add_dep in extra_deps[extra_dep]:
                    ops[f'{var}{dep}']['dep'].append(f'{add_dep.lower()}')
            else:
                added_deps = [i.lower() for i in extra_deps[extra_dep]]
                ops[f'{var}{dep}'] = {'file': '', 'dep': added_deps}

    return ops


def translate_isa(isa: str, op_dir: str, extra_exts: list) -> list:
    # ISA is case-insensitive
    isa = isa.lower()

    # extract bit width
    if isa.startswith('rv32'):
        bit_width = 32
        isa = isa[4:]
    elif isa.startswith('rv64'):
        bit_width = 64
        isa = isa[4:]
    elif isa.startswith('rv128'):
        bit_width = 128
        isa = isa[5:]
    else:
        sys.exit(-1)

    # parse extensions
    exts = extra_exts.copy()
    curr_ext = ''
    for char in isa:
        if char == '_':
            exts.append(curr_ext)
            curr_ext = ''
        elif char == 'x' or char == 'z' or curr_ext != '':
            curr_ext += char
        else:
            exts.append(char)
    # append last possible custom extension
    if curr_ext != '':
        exts.append(curr_ext)

    # read in op-database
    ops = add_dependencies(read_all_ops(op_dir), 'util/isa.json')

    # translate
    files = []
    ext_op_files(exts, files, bit_width, ops)

    # add prefix
    files = [f'{op_dir}/{i}' for i in files]

    return sorted(list(set(files)))


def main():
    """Assemble OP codes from ISA string"""
    # Parse Arguments
    parser = argparse.ArgumentParser(
        prog='analyze_opcodes',
        description='A tool to assemble RISC-V opcodes from the ISA string',
    )
    parser.add_argument('--op_dir', dest='op_dir', required=True,
                        help='The opcode directory.')
    parser.add_argument('--pseudo', dest='pseudo', nargs='*',
                        help='If pseudo instructions should be enabled.')
    parser.add_argument('--system', dest='system', action='store_true',
                        help='If system instructions should be enabled.')
    parser.add_argument('--custom', dest='custom', action='store_true',
                        help='If custom instructions should be enabled.')
    parser.add_argument(dest='isa', help='ISA string.')
    args = parser.parse_args()

    extra_ops = []
    if args.pseudo:
        extra_ops.extend(args.pseudo)
    if args.system:
        extra_ops.append('system')
    if args.custom:
        extra_ops.append('custom')

    print(' '.join(translate_isa(args.isa, args.op_dir, extra_ops)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
