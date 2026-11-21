#!/usr/bin/env python3
"""Build reproducible allowlisted public and organizer archives."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)

PUBLIC_FILES = (
    'README.md',
    'Makefile',
    'security_controller.v',
    'auth_fsm.v',
    'access_control.v',
    'debug_fsm_netlist.v',
    'tb_starter.v',
    'encode_actions.py',
    'example_inputs.txt',
)
PRIVATE_FILES = (
    'ORGANIZER_NOTES.md',
    'HINTS_FOR_CTFD.md',
    'debug_fsm.v',
    'reference_exploit.txt',
    'wrong_key.txt',
    'near_key.txt',
    'legitimate_login.txt',
    'bad_password.txt',
    'premature_reset.txt',
    'flag.txt',
    'sixtyfour.txt',
    'sixtyfive.txt',
    'comments.txt',
    'invalid_x.txt',
    'invalid_z.txt',
    'invalid_control.txt',
    'malformed.txt',
)
TOOL_FILES = (
    'audit_public.py',
    'test_netlist_text.py',
    'selfcheck.py',
    'generate_compat_netlist.py',
    'build_yosys_netlist.sh',
    'pack_release.py',
)

# Fail closed: a new public file must be reviewed and added to the allowlist.
actual = {p.name for p in (ROOT/'public').iterdir()}
assert actual == set(PUBLIC_FILES), (actual - set(PUBLIC_FILES), set(PUBLIC_FILES) - actual)
assert all((ROOT/'private'/x).is_file() for x in PRIVATE_FILES)
assert all((ROOT/'tools'/x).is_file() for x in TOOL_FILES)
public = [(ROOT/'public'/name, name) for name in PUBLIC_FILES]
organizer = ([(p, 'public/' + name) for p, name in public] +
             [(ROOT/'private'/name, 'private/' + name) for name in PRIVATE_FILES] +
             [(ROOT/'tools'/name, 'tools/' + name) for name in TOOL_FILES] +
             [(ROOT/'Makefile', 'Makefile')])

def create_zip(filename, entries):
    with ZipFile(DIST/filename, 'w', ZIP_DEFLATED) as archive:
        for source, dest in entries:
            archive.write(source, dest)
    with ZipFile(DIST/filename) as archive:
        assert set(archive.namelist()) == {dest for _,dest in entries}
    print(f'Created {DIST/filename} ({len(entries)} reviewed files)')

create_zip('backdoor_ctf_v2_public.zip', public)
create_zip('backdoor_ctf_v2_organizer.zip', organizer)
