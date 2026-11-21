#!/usr/bin/env python3
"""Generate a generic simulated gate network when Yosys is unavailable.

The fallback implementation obscures individual key literals inside mixed
multi-input gates. It is not a substitute for the final Yosys release netlist.
"""
from pathlib import Path
import random
import re

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / 'private/debug_fsm.v'
TARGET = ROOT / 'public/debug_fsm_netlist.v'
match = re.search(r"DBG_KEY\s*=\s*32'h([0-9a-fA-F]{8})", PRIVATE.read_text())
if not match:
    raise SystemExit('Private DBG_KEY declaration not found')
key = int(match.group(1), 16)
rng = random.Random(20261121)
ids = iter(rng.sample(range(1000, 9999), 240))
statements = []
wires = []

def w():
    name = f'w{next(ids)}'
    wires.append(name)
    return name

def put(expr):
    name = w()
    statements.append(f'    assign {name} = {expr};')
    return name

def not_(a): return put(f'~({a})')
def and_(*args):
    assert len(args) >= 2
    return put('(' + ' & '.join(args) + ')')
def or_(*args):
    assert len(args) >= 2
    return put('(' + ' | '.join(args) + ')')

# Eight mixed four-bit gates, in randomized bit order. There are no
# trivial one-bit assigns of the form w = ~dbg_data[N] from which grep
# can reconstruct the key with one pass.
bits = list(range(32))
rng.shuffle(bits)
terms = []
for i in range(0, 32, 4):
    group = bits[i:i + 4]
    if rng.choice((False, True)):
        # Direct AND of four required literals.
        literals = [f'dbg_data[{b}]' if (key >> b) & 1 else f'~dbg_data[{b}]'
                    for b in group]
        terms.append(put('(' + ' & '.join(literals) + ')'))
    else:
        # De Morgan equivalent: NOR of four mismatched literals.
        mismatches = [f'~dbg_data[{b}]' if (key >> b) & 1 else f'dbg_data[{b}]'
                      for b in group]
        terms.append(put('~(' + ' | '.join(mismatches) + ')'))
while len(terms) > 1:
    merged = []
    for i in range(0, len(terms), 2):
        merged.append(and_(*terms[i:i + 2]))
    terms = merged
key_ok = terms[0]

# Three one-hot state flops, with non-semantic internal identifiers.
regnames = [f'q{next(ids)}' for _ in range(3)]
locked, armed, active = regnames
ent_auth = and_('diag_en', 'auth_ok')
ent_dbg = and_('diag_en', 'auth_check', not_('pw_valid'), key_ok, not_('soft_rst'))
ent_dbg_prio = and_(ent_dbg, not_(ent_auth))
hold_lock = and_(not_(ent_auth), not_(ent_dbg))
fall_lock = or_('auth_fail', and_(not_('auth_check'), not_('diag_en')))
d_locked = or_(and_(locked, hold_lock), and_(armed, fall_lock))
d_armed = or_(and_(locked, ent_dbg_prio), and_(armed, not_('auth_fail'), 'auth_check'))
d_active = or_(active, and_(locked, ent_auth), and_(armed, not_('auth_fail'), not_('auth_check'), 'diag_en'))
rng.shuffle(statements)

lines = [
    '`timescale 1ns/1ps',
    'module debug_fsm (',
    '    input wire clk, input wire rst_n, input wire soft_rst,',
    '    input wire diag_en, input wire [31:0] dbg_data,',
    '    input wire auth_check, input wire auth_ok,',
    '    input wire auth_fail, input wire pw_valid,',
    '    output wire dbg_bypass',
    ');',
]
lines.extend(f'    wire {name};' for name in wires)
lines.extend(f'    reg {name};' for name in regnames)
lines.extend(statements)
lines.extend([
    '    always @(posedge clk or negedge rst_n) begin',
    '        if (!rst_n) begin',
    f"            {locked} <= 1'b1;",
    f"            {armed} <= 1'b0;",
    f"            {active} <= 1'b0;",
    '        end else begin',
    f'            {locked} <= {d_locked};',
    f'            {armed} <= {d_armed};',
    f'            {active} <= {d_active};',
    '        end',
    '    end',
    f'    assign dbg_bypass = {active};',
    'endmodule',
    '',
])
TARGET.write_text('\n'.join(lines))
print(f'Wrote fallback netlist: {TARGET} ({len(wires)} internal wires)')
