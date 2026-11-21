#!/usr/bin/env python3
"""Interpret this project's standalone generic gate netlist for 2-valued tests.

This is a restricted expression interpreter for our fallback circuit, NOT an
HDL compiler or a substitute for the mandatory Icarus Verilog release check.
Yosys-generated netlists may use constructs beyond this interpreter.
"""
from pathlib import Path
import ast
import importlib.util
import io
import contextlib
import itertools
import re
import sys
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
with contextlib.redirect_stdout(io.StringIO()):
    spec=importlib.util.spec_from_file_location('selfcheck', ROOT/'tools/selfcheck.py')
    model=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)

text=(ROOT/'public/debug_fsm_netlist.v').read_text()
if not re.search(r'\breg\s+q\d+\s*;', text):
    print('NOTE: non-fallback netlist detected; skip fallback-only text interpreter')
    raise SystemExit(0)
assigns=dict(re.findall(r'assign\s+(w\d+)\s*=\s*([^;]+);',text))
regnames=re.findall(r'\breg\s+(q\d+)\s*;',text)
assert len(regnames)==3 and len(assigns)>25
flops=re.findall(r'(q\d+)\s*<=\s*(w\d+);',text)
assert len(flops)==3
next_states=dict(flops)
reset_states=dict((name,int(b)) for name,b in re.findall(r"(q\d+)\s*<=\s*1'b([01]);",text))
assert set(reset_states)==set(regnames) and set(next_states)==set(regnames)
assert sorted(reset_states.values())==[0,0,1]
output=re.search(r'assign\s+dbg_bypass\s*=\s*(q\d+);',text).group(1)
locked=next(r for r in regnames if reset_states[r]==1)
active=output
armed=next(r for r in regnames if r not in {locked,active})

class Walker(ast.NodeVisitor):
    def __init__(self,lookup): self.lookup=lookup
    def visit_Name(self,node):return bool(self.lookup(node.id))
    def visit_Constant(self,node):
        assert isinstance(node.value, bool)
        return node.value
    def visit_UnaryOp(self,node):
        assert isinstance(node.op,ast.Not)
        return not self.visit(node.operand)
    def visit_BoolOp(self,node):
        vals=[self.visit(n) for n in node.values]
        if isinstance(node.op,ast.And):return all(vals)
        if isinstance(node.op,ast.Or):return any(vals)
        raise AssertionError(type(node.op))
    def generic_visit(self,node):raise AssertionError(f'unsupported logic: {ast.dump(node)}')

def evaluate(reg_state, inp):
    soft,req,diag,valid,pw,token=inp
    check=reg_state['auth_state']==1
    ok=reg_state['auth_state']==2
    fail=check and valid and pw!=model.DEMO and not soft
    env={
        'soft_rst':bool(soft),'diag_en':bool(diag),
        'auth_check':check,'auth_ok':ok,'auth_fail':fail,
        'pw_valid':bool(valid),
        locked:reg_state['debug_state']==0,
        armed:reg_state['debug_state']==1,
        active:reg_state['debug_state']==2,
    }
    cache={}
    def resolve(name):
        if name in env:return env[name]
        if name in cache:return cache[name]
        assert name in assigns, name
        expr=assigns[name]
        expr=re.sub(r'dbg_data\[(\d+)\]',lambda m:'True' if token & (1<<int(m.group(1))) else 'False',expr)
        expr=expr.replace('~',' not ').replace('&',' and ').replace('|',' or ').strip()
        value=Walker(resolve).visit(ast.parse(expr, mode='eval').body)
        cache[name]=value
        return value
    out=[bool(resolve(next_states[name])) for name in (locked,armed,active)]
    assert sum(out)==1,(reg_state,inp,out)
    return out.index(True)

n=0
for auth,debug in itertools.product(range(3),range(3)):
    for soft,req,diag,valid,good,key_ok in itertools.product((0,1), repeat=6):
        inp=(soft,req,diag,valid,model.DEMO if good else 0,model.KEY if key_ok else 0)
        actual=evaluate({'auth_state':auth,'debug_state':debug},inp)
        expected=model.debug_step(debug,auth,inp)
        assert actual==expected,(auth,debug,inp,actual,expected)
        n+=1
print(f'PASS: interpreted released gate-netlist text matches RTL model in {n} input/state cases')

# Full 32-bit comparator sensitivity, against the generated network itself.
for bit in range(32):
    inp = (0, 0, 1, 0, 0, model.KEY ^ (1 << bit))
    assert evaluate({'auth_state': 1, 'debug_state': 0}, inp) == 0, bit
print('PASS: netlist comparator rejects every single-bit key mutation')
