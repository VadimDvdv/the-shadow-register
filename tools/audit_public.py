#!/usr/bin/env python3
"""Fail-closed audit of precisely the nine approved public files."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT/'public'
ALLOWED = {
    'README.md', 'Makefile', 'security_controller.v', 'auth_fsm.v',
    'access_control.v', 'debug_fsm_netlist.v', 'tb_starter.v',
    'encode_actions.py', 'example_inputs.txt',
}
assert PUBLIC.is_dir()
actual = {p.name for p in PUBLIC.iterdir()}
assert actual == ALLOWED, f'Unexpected/missing public entries: +{actual-ALLOWED}, -{ALLOWED-actual}'
assert all((PUBLIC/name).is_file() for name in ALLOWED)

SECRET = (ROOT/'private/flag.txt').read_text().strip()
KEY = re.search(r"DBG_KEY\s*=\s*32'h([0-9a-fA-F]{8})",
                (ROOT/'private/debug_fsm.v').read_text()).group(1).upper()
for filename in sorted(ALLOWED):
    contents = (PUBLIC/filename).read_bytes()
    assert b'\x00' not in contents, (filename, 'binary public file')
    s = contents.decode('utf-8')
    assert SECRET not in s, (filename, 'flag disclosed')
    assert KEY not in s.upper(), (filename, 'key string disclosed')
    assert not re.search(r'\bDBG_KEY\b', s), (filename, 'key name disclosed')
    assert 'ORGANIZER ONLY' not in s, (filename, 'organizer marker disclosed')

net = (PUBLIC/'debug_fsm_netlist.v').read_text()
assert not re.search(r'assign\s+\w+\s*=\s*~?\s*dbg_data\[\d+\]\s*;', net), \
    'Trivial isolated comparator-input bit assignment found'
print('PASS: public allowlist, sensitive-content scan, and netlist grep audit')
