#!/usr/bin/env python3
"""Independent Python state-model checks, not a replacement for iverilog/Yosys."""
from collections import deque
from itertools import product
from pathlib import Path
import importlib.util
import sys
import re
sys.dont_write_bytecode = True

ROOT=Path(__file__).resolve().parents[1]
KEY=int(re.search(r"DBG_KEY\s*=\s*32'h([0-9A-Fa-f]{8})",(ROOT/'private/debug_fsm.v').read_text()).group(1),16)
# The public action alphabet is the one and only authoritative mapping.
spec = importlib.util.spec_from_file_location('encode_actions', ROOT/'public/encode_actions.py')
encoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(encoder)
DEMO = encoder.DEMO_PASSWORD
ACTIONS = {name: encoder.vector_for(name, KEY) for name in encoder.ACTIONS}
assert len(ACTIONS) == 6
assert len(set(ACTIONS.values())) == len(ACTIONS), 'Action vectors must be distinct'

# Verify the README table and the actual flag are aligned with the encoder.
readme = (ROOT/'public/README.md').read_text()
table_names = set(re.findall(r'^\|\s*([A-Z][A-Z0-9_]*)\s*\|', readme, re.M))
assert table_names == set(ACTIONS), (table_names, set(ACTIONS))

def parse_vector(line):
    words = line.split()
    assert len(words) == 6, line
    return tuple(int(x) for x in words[:4]) + (int(words[4], 16), int(words[5], 16))

reference_vectors = [parse_vector(line) for line in (ROOT/'private/reference_exploit.txt').read_text().splitlines() if line.strip()]
reverse_actions = {vector: name for name, vector in ACTIONS.items()}
reference_words = tuple(reverse_actions[vector] for vector in reference_vectors)
expected_flag = 'CTF{' + '_'.join(reference_words) + f'_{KEY:08X}' + '}'
actual_flag = (ROOT/'private/flag.txt').read_text().strip()
assert actual_flag == expected_flag, (actual_flag, expected_flag)
print('PASS: README action names, encoder, reference vectors, and static flag match')

# Authentication states: 0=IDLE,1=CHECK,2=AUTH_OK
# Debug states: 0=LOCKED,1=ARMED,2=ACTIVE

def auth_step(a, inp):
    soft,req,diag,valid,pw,token=inp
    if soft: return 0
    if a==0: return 1 if req else 0
    if a==1: return (2 if pw==DEMO else 0) if valid else 1
    return 2

def debug_step(d,a,inp):
    soft,req,diag,valid,pw,token=inp
    check=a==1; ok=a==2
    fail=check and valid and (pw!=DEMO) and not soft
    key_ok=token==KEY
    if d==0:
        if diag and ok: return 2
        if diag and check and not valid and key_ok and not soft: return 1
        return 0
    if d==1:
        if fail: return 0
        if not check: return 2 if diag else 0
        return 1
    return 2

def gates_step(d,a,inp):
    soft,req,diag,valid,pw,token=inp
    check=a==1; ok=a==2
    fail=check and valid and (pw!=DEMO) and not soft
    key_ok=token==KEY
    l,r,t=(int(d==i) for i in range(3))
    ent_auth=diag and ok
    ent_dbg=diag and check and not valid and key_ok and not soft
    next_l=(l and not ent_auth and not ent_dbg) or (r and (fail or (not check and not diag)))
    next_r=(l and ent_dbg and not ent_auth) or (r and not fail and check)
    next_t=t or (l and ent_auth) or (r and not fail and not check and diag)
    bits=[bool(next_l),bool(next_r),bool(next_t)]
    assert sum(bits)==1, (d,a,inp,bits)
    return bits.index(True)

def step(st,inp):
    a,d,ever=st
    na=auth_step(a,inp)
    nd=debug_step(d,a,inp)
    assert gates_step(d,a,inp)==nd,(st,inp)
    ever=ever or na==2
    return (na,nd,ever),bool(nd==2 and not ever)

start=(0,0,False)
# Explore reachable joint states with unconstrained simultaneous control inputs.
seen={start}; todo=deque([start]); checks=0
while todo:
    st=todo.popleft()
    for soft,req,diag,valid,good,has_key in product((0,1),repeat=6):
        pw=DEMO if good else 0
        token=KEY if has_key else 0
        nxt,_=step(st,(soft,req,diag,valid,pw,token))
        checks+=1
        if nxt not in seen:
            seen.add(nxt);todo.append(nxt)
print(f'PASS: original/gate equations equivalent for {checks} reachable-state input cases ({len(seen)} joint states)')

# The distributed netlist is intentionally not assumed to have a particular
# per-bit comparator representation. tools/test_netlist_text.py interprets
# the fallback gates; make check exercises the actual HDL for either netlist.

# Exhaustive enumeration through length four: unlike state-pruned BFS, this
# counts every distinct shortest action trace, even if two share a state.
for depth in range(1,len(reference_words)+1):
    wins=[]
    for seq in product(ACTIONS,repeat=depth):
        st=start
        succeeded=False
        for name in seq:
            st,found=step(st,ACTIONS[name])
            succeeded = succeeded or found
        if succeeded: wins.append(seq)
    if depth < len(reference_words):
        assert not wins, (depth,wins)
    else:
        assert wins == [reference_words], wins
        print(f'PASS: exhaustive six-action traces through depth {depth}: one shortest solution')

# Test all action traces in an abstract model where no submitted diag_data matches KEY.
frontier={start}
for depth in range(8):
    next_frontier=set()
    for st in frontier:
        for name,inp in ACTIONS.items():
            no_key_inp=inp[:5]+(0,)
            nxt,success=step(st,no_key_inp)
            assert not success,(depth,name,st)
            next_frontier.add(nxt)
    frontier=next_frontier
print('PASS: incorrect diagnostic data cannot generate an unauthorized bypass')
# Each bit is required by the full-word diagnostic-key comparator.
for bit in range(32):
    st = start
    wrong = KEY ^ (1 << bit)
    bypass = False
    for v in reference_vectors:
        candidate = v[:5] + (wrong if v[2] else 0,)
        st, success = step(st, candidate)
        bypass |= success
    assert not bypass, f'bit {bit} can be flipped without preventing bypass'
print('PASS: all 32 one-bit diagnostic key mutations reject the bypass')


# Validate the reference, password-rejection, and normal-login controls.
for path,expected in [
    ('reference_exploit.txt',True),('wrong_key.txt',False),
    ('legitimate_login.txt',False),('bad_password.txt',False),
    ('premature_reset.txt',False), ('near_key.txt',False),
]:
    st=start; bypass=False
    for line in (ROOT/'private'/path).read_text().splitlines():
        soft,req,diag,valid,pw,token=line.split()
        st,ok=step(st,(int(soft),int(req),int(diag),int(valid),int(pw,16),int(token,16)))
        bypass|=ok
    assert bypass==expected,(path,bypass,expected)
    print(f'PASS: {path} -> {"bypass" if bypass else "no bypass"}')
print('All model-level checks passed. Run make check for HDL simulation too.')
