#!/usr/env python3
# Copyright 2023 ETH Zurich and University of Bologna.
# Solderpad Hardware License, Version 0.51, see LICENSE for details.
# SPDX-License-Identifier: SHL-0.51

# Authors:
# - Thomas Benz <tbenz@iis.ee.ethz.ch>

"""Lint RISC-V opcodes"""
import argparse
import collections
import re
import subprocess
import sys
import flatdict
from mako.template import Template


GENABLE_ENTITIES = ['clash_matrix', 'inst_table', 'free_table']


OPCODE_REGEX = r'  localparam logic \[31\:0\] +([0-9A-Za-z_\.]+) += +32\'b([?01]+);'


INST_TABLE_TEMPLATE = '''
\\begin{table} \\centering
    \\renewcommand{\\arraystretch}{1.1}
    \\resizebox{\\textwidth}{!}{% use resizebox with textwidth
        \\begin{tabular}{lllllllllllllll}
            \\textbf{Instruction Name} & \\textbf{Extension} & \\textbf{Type} & \\textbf{Funct7} &
            \\textbf{RS1} & \\textbf{RS2} & \\textbf{Funct3} & \\textbf{RD} & \\textbf{OPC} &
            \\textbf{Quad} & \\textbf{Instuction Clash List} & \\textbf{Spec Clash List} &
            \\textbf{QuadOk} & \\textbf{OpOk} & \\textbf{FunctOk} <%text>\\\\</%text>
            \\toprule
${content}
        \\end{tabular}
    }
\\end{table}
'''


TICK_BAD = ['\\bad', '\\tick']


# Allowed custom opcode space
SPEC_CUST_QUAD = ['11']
SPEC_CUST_OPC = ['00010', '01010', '10110', '11110']
SPEC_CUST_FUNC3 = ['000', '010', '011', '100', '110', '111', '??0', '?00', '?10', '0?0']


def nested_dict():
    """Returns a nested dict objects"""
    return collections.defaultdict(nested_dict)


def sym_to_hex(symbol: str) -> str:
    """Prints a symbol with 0, 1, ? to a string"""
    res = '0x'
    if len(symbol) % 4 != 0:
        symbol = '0' * (4 - len(symbol) % 4) + symbol

    for idx in range(0, len(symbol), 4):
        if '?' in symbol[idx:idx+4]:
            res += '.'
        else:
            res += hex(int(symbol[idx:idx+4], 2))[2:]
    return res


def match_symbols(sym_a: str, sym_b: str) -> bool:
    """Matches two symbols containing 0, 1, ?"""
    if len(sym_a) != len(sym_b):
        print(f'Mismatch in symbol length between {sym_a} and {sym_b}')
        sys.exit(-1)

    if sym_a == sym_b:
        return 1

    match = 1
    for i in range(0, len(sym_a)):
        if sym_a[i] == '?' or sym_b[i] == '?':
            match &= 1
        else:
            match &= sym_a[i] == sym_b[i]
    return match


def read_opcodes(op_files: list, op_sorted: bool) -> list:
    """Read the selected opcode sets"""
    # use a nested dict to sort
    opmap = nested_dict()

    for op_file in op_files:
        # get the data
        name = op_file[8:]
        output = subprocess.getoutput(f'python3 util/parse_opcodes -sverilog {op_file}')
        codes = re.findall(OPCODE_REGEX, output)

        # decompose
        for code in codes:
            f_1_0 = code[1][-2:]        # opcode: quadrant
            f_6_2 = code[1][-7:-2]      # opcode
            f_11_7 = code[1][-12:-7]    # rd
            f_14_12 = code[1][-15:-12]  # funct3
            f_19_15 = code[1][-20:-15]  # rs1
            f_24_20 = code[1][-25:-20]  # rs2
            f_31_25 = code[1][-32:-25]  # funct7

            # add to dict to be sorted in sorting order
            opmap[f_1_0][f_6_2][f_14_12][f_31_25][f_11_7][f_19_15][f_24_20][code[0]][name]

    # sort and unpack
    opcodes = []
    opmap = flatdict.FlatDict(opmap, delimiter='.')
    if op_sorted:
        opmap = sorted(opmap.keys())

    for curr_op in opmap:
        fields = curr_op.split('.')

        # detect custom extensions
        spec = fields[8]
        # extract extension specifiers
        ext_spec = ''.join([i[0] for i in fields[8].split('_')[1:]])
        if 'x' in ext_spec:
            ext_type = 'CUSTOM'
        elif 'z' in ext_spec:
            ext_type = 'DRAFT'
        else:
            ext_type = 'SPECIFICATION'

        inst = fields[7]
        fields = [fields[3], fields[6], fields[5], fields[2], fields[4], fields[1], fields[0]]
        fields_hex = [sym_to_hex(i) for i in fields]
        opcodes.append({'inst': inst, 'spec': spec, 'type': ext_type, 'f': fields, 'h': fields_hex})

    return opcodes


def analyze_clashes(opcodes: list) -> dict:
    """Analyze clashes of the opcode space"""
    clash_inst = {}
    clash_spec = {}
    clash_cnts = {}
    total_clashes = 0

    for op in opcodes:

        # per-instruction bookkeeping
        clashes_inst = []
        clashes_spec = []
        clashes_cnts = {}

        # all-to-all comparison
        for op_now in opcodes:

            # check if the two opcodes overlap
            match = 1
            for i in range(0, 7):
                match &= match_symbols(op['f'][i], op_now['f'][i])

            # add clashes
            if match and op['inst'] != op_now['inst']:
                clashes_inst.append(op_now['inst'])
                clashes_spec.append(op_now['spec'])
                if not op_now['spec'] in clashes_cnts:
                    clashes_cnts[op_now['spec']] = 0
                clashes_cnts[op_now['spec']] += 1
                total_clashes += 1

        # keep track of overall clashes
        clash_inst[op['inst']] = clashes_inst

        # extensions
        if not op['spec'] in clash_spec:
            clash_spec[op['spec']] = []
        clash_spec[op['spec']].extend(clashes_spec)
        clash_spec[op['spec']] = list(set(clash_spec[op['spec']]))

        # add count
        if not op['spec'] in clash_cnts:
            clash_cnts[op['spec']] = clashes_cnts
        else:
            for inst in clashes_cnts:
                if inst not in clash_cnts[op['spec']]:
                    clash_cnts[op['spec']][inst] = clashes_cnts[inst]
                else:
                    clash_cnts[op['spec']][inst] += clashes_cnts[inst]

    return {'inst': clash_inst, 'spec': clash_spec, 'cnts': clash_cnts, 'tot': total_clashes}


def lint_custom_exts(opcodes: list) -> dict:
    """Lint our custom extensions"""
    not_allowed = {}

    for op in opcodes:

        # determine if an extension is allowed
        allowed = 1
        if op['type'] == 'CUSTOM':
            # check quadrant
            proper_quadrant = 0
            for allquad in SPEC_CUST_QUAD:
                proper_quadrant |= match_symbols(op['f'][6], allquad)
            allowed &= proper_quadrant

            # check opcode
            op_allowed = 0
            for allop in SPEC_CUST_OPC:
                op_allowed |= match_symbols(op['f'][5], allop)
            allowed &= op_allowed

            # check funct field
            func_allowed = 0
            for allfunc in SPEC_CUST_FUNC3:
                func_allowed |= match_symbols(op['f'][3], allfunc)
            allowed &= func_allowed

        if not allowed:
            if not op['spec'] in not_allowed:
                not_allowed[op['spec']] = {}
            not_allowed[op['spec']][op['inst']] = {'quad': int(proper_quadrant), 'opc': op_allowed,
                                                   'func': func_allowed}

    return not_allowed


def render_clash_table(opcodes: dict, clashes: dict, custom_exts: dict) -> str:
    """Render a LATEX table showing the clashes"""
    headers = {}
    specs = []

    # color headers
    for op in opcodes:
        if op['spec'] not in specs:
            specs.append(op['spec'])
            # linting issues
            if op['spec'] in custom_exts:
                headers[op['spec']] = f'\\color{{orange}}{{{op["spec"]}}}'
            elif op['type'] == 'DRAFT':
                headers[op['spec']] = f'\\color{{gray}}{{{op["spec"]}}}'
            elif op['type'] == 'CUSTOM':
                headers[op['spec']] = f'\\color{{blue}}{{{op["spec"]}}}'
            else:
                headers[op['spec']] = f'\\color{{black}}{{{op["spec"]}}}'

    # Only render upper half of matrix
    # Add a green tick if there are no clashes, add the amount of clashes in red else
    rows = ''
    for ext in clashes['spec'].keys():
        lower = 1
        for ext_inner in clashes['spec'].keys():
            if ext == ext_inner:
                rows += '\\own & '
                lower = 0
            elif ext_inner in clashes['spec'][ext]:
                if not lower:
                    rows += f'\\color{{red}}{{{clashes["cnts"][ext_inner][ext]}}} & '
                else:
                    rows += ' & '
            else:
                if not lower:
                    rows += '\\tick & '
                else:
                    rows += ' & '

        rows = rows + f'{headers[ext]}\\\\\n            '

    # format rotated headers
    rot_headers = ' & '.join([f'\\rotatebox{{90}}{{{i}}}' for i in headers.values()]) + ' & \\\\'

    context = {
        'tabs': 'c' * len(clashes['spec']) + 'l',
        'headers': f'            {rot_headers}',
        'content': f'            {rows}'
    }

    # render
    with open('util/clash-table.tex.tpl', 'r', encoding='utf-8') as templ_file:
        table_tpl = templ_file.read()
    return Template(table_tpl).render(**context).replace('_', '\\_')


def render_inst_table(opcodes: dict, clashes: dict, custom_exts: dict) -> str:
    """Render a LATEX table showing all instructions"""
    content = ''
    page = ''
    lines = 0

    for op_idx in range(len(opcodes)):

        # fetch opcode
        op = opcodes[op_idx]

        # clashes
        clashes_inst = clashes['inst'][op["inst"]]
        if len(clashes_inst) == 0:
            clashes_spec = []
        else:
            clashes_spec = clashes['spec'][op["spec"]]

        # issues with custom extensions
        if op["spec"] in custom_exts and op["inst"] in custom_exts[op["spec"]]:
            extensions = custom_exts[op["spec"]][op["inst"]]
        else:
            extensions = {}

        line = ''

        line += f'{op["inst"]} & {op["spec"]} & {op["type"]} & {op["f"][0]} & {op["f"][1]} & '
        line += f'{op["f"][2]} & {op["f"][3]} & {op["f"][4]} & {op["f"][5]} & {op["f"][6]} & '

        max_added_lines = 0

        if len(clashes_inst) > 0:
            added_lines = 0
            line += '\\makecell[l]{ '
            for cinst in clashes_inst:
                line += f'{cinst} \\\\ '
                added_lines += 1
            line = line[:-3] + '} & '
            max_added_lines = max(max_added_lines, added_lines)

            added_lines = 0
            line += '\\makecell[l]{ '
            for cspec in clashes_spec:
                line += f'{cspec}  \\\\ '
                added_lines += 1
            line = line[:-3] + '} & '
            max_added_lines = max(max_added_lines, added_lines)
        else:
            line += ' \\tick & \\tick & '
            max_added_lines += 1

        lines += max_added_lines

        if len(extensions) > 0:
            for ext in extensions:
                line += f'{TICK_BAD[extensions[ext]]} & '
            line = line[:-3]
        else:
            line += ' \\tick & \\tick & \\tick '

        line += ' \\\\ \\midrule\n            '

        # decide when to render page now
        if lines > 31 and op_idx != len(opcodes)-1:
            # render
            content += Template(INST_TABLE_TEMPLATE).render(content=page)
            content += '\n\\newpage\n\\clearpage\n'
            page = ''
            lines = max_added_lines

        page += line

        # decide to render last page
        if op_idx == len(opcodes)-1:
            # render
            content += Template(INST_TABLE_TEMPLATE).render(content=page)
            content += '\n\\newpage\n\\clearpage\n'
            page = ''
            lines = 0

    # render
    with open('util/inst-table.tex.tpl', 'r', encoding='utf-8') as templ_file:
        table_tpl = templ_file.read()
    return Template(table_tpl).render(content=content).replace('_', '\\_')


def generate_all_opcodes(spec_only: bool) -> list:
    """Generate a list of all possible op codes"""
    possible_ops = []
    for quad in range(0, 2**2):
        quad = f'{quad:02b}'
        for opc in range(0, 2**5):
            opc = f'{opc:05b}'
            for func3 in range(0, 2**3):
                func3 = f'{func3:03b}'

                # check if its part of the custom insts
                is_spec = True
                if spec_only:
                    quad_ok = False
                    for allquad in SPEC_CUST_QUAD:
                        quad_ok |= match_symbols(quad, allquad)
                    is_spec &= quad_ok
                    opc_ok = False
                    for allopc in SPEC_CUST_OPC:
                        opc_ok |= match_symbols(opc, allopc)
                    is_spec &= opc_ok
                    func3_ok = False
                    for allfunc3 in SPEC_CUST_FUNC3:
                        func3_ok |= match_symbols(func3, allfunc3)
                    is_spec &= func3_ok

                for func7 in range(0, 2**7):
                    func7 = f'{func7:07b}'

                    # append
                    if is_spec:
                        possible_ops.append([func7, '?????', '?????', func3, '?????', opc, quad])

    return possible_ops


def determine_free_ops(all_opcodes: dict, possible_ops: list) -> list:
    """Determine which op codes are free"""
    pops = possible_ops.copy()
    for op in all_opcodes:
        for pos_op in possible_ops:
            # check if opcode matches
            match = True
            for f_idx in range(0, 7):
                match &= match_symbols(op['f'][f_idx], pos_op[f_idx])
            if match:
                pops.remove(pos_op)
        possible_ops = pops.copy()
    return pops


def num_sub_free(free: dict) -> int:
    """Returns the number of free opcodes"""
    num_free = 0
    flat = flatdict.FlatDict(free, delimiter='.')
    for ele in flat:
        num_free += len(flat[ele])
    return num_free


def render_free_table(free_opcodes: list) -> list:
    """Render a LATEX table with all free opcodes"""
    free = nested_dict()

    # reorganize and group
    for fop in free_opcodes:
        if not isinstance(free[fop[6]][fop[5]][fop[3]], list):
            free[fop[6]][fop[5]][fop[3]] = []
        free[fop[6]][fop[5]][fop[3]].append(sym_to_hex(fop[0]))

    content = ''
    # write report
    for quad in free:
        num_quad = num_sub_free(free[quad])
        content += f'\\section{{Quadrant {sym_to_hex(quad)}: {num_quad} Free}}\n'

        for opc in free[quad]:
            num_opc = num_sub_free(free[quad][opc])
            content += f'\\subsection{{Opcode {sym_to_hex(opc)}: {num_opc} Free}}\n'

            for func3 in free[quad][opc]:
                num_func3 = len(free[quad][opc][func3])
                content += f'\\subsubsection{{Funct3 {sym_to_hex(func3)}: {num_func3}/128 Free}}\n'

                func7_str = ''
                for pop in range(0, 2**7):
                    pop_h = f'0x{pop:02x}'
                    if pop_h in free[quad][opc][func3]:
                        func7_str += f'\\textcolor{{green}}{{{pop_h}}}, '
                    else:
                        func7_str += f'\\textcolor{{red}}{{{pop_h}}}, '
                    if pop % 16 == 15 and pop > 0:
                        func7_str = func7_str[:-2] + '\n\n'

                content += func7_str[:-1] + '\n\n'

    # render
    with open('util/free-table.tex.tpl', 'r', encoding='utf-8') as templ_file:
        table_tpl = templ_file.read()
    return Template(table_tpl).render(content=content).replace('_', '\\_')


def main():
    """Main: parse arguments"""
    # Parse Arguments
    parser = argparse.ArgumentParser(
        prog='analyze_opcodes',
        description='A tool to analyze RISC-V opcodes',
    )
    parser.add_argument('--report', choices=sorted(GENABLE_ENTITIES), dest='report', required=True,
                        help='The report to render.')
    parser.add_argument('--exp_clashes', dest='expc', required=True,
                        help='The number of clashes expected.')
    parser.add_argument('--exp_wrong_insts', dest='expi', required=True,
                        help='The number of wrong extensions expected.')
    parser.add_argument(dest='opfiles', nargs='*', help='opcode files')
    args = parser.parse_args()

    # analysis
    opcodes = read_opcodes(args.opfiles, True)

    clashes = analyze_clashes(opcodes)
    custom_exts = lint_custom_exts(opcodes)

    # visualization
    if args.report == 'clash_matrix':
        print(render_clash_table(opcodes, clashes, custom_exts))
    elif args.report == 'inst_table':
        print(render_inst_table(opcodes, clashes, custom_exts))
    elif args.report == 'free_table':
        all_opcodes = generate_all_opcodes(spec_only=True)
        free_opcodes = determine_free_ops(opcodes, all_opcodes)
        print(render_free_table(free_opcodes))
    else:
        print('Unknown report', file=sys.stderr)
        return -1

    # return
    if int(args.expc) != -1 and clashes['tot'] != int(args.expc):
        print(f'Expected clashes mismatch: {clashes["tot"]} instead of {args.expc}',
              file=sys.stderr)
        return -1

    if int(args.expi) != -1 and len(custom_exts) != int(args.expi):
        print(f'Expected wrong instructions mismatches: {len(custom_exts)} instead of {args.expi}',
              file=sys.stderr)
        return -1

    # otherwise it works
    return 0


if __name__ == '__main__':
    sys.exit(main())
