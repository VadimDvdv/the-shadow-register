#!/usr/bin/env python3

# Usage: python3 encode_actions.py --key <8-digit-hex-key> ACTION1 ACTION2 ...
# Example: python3 encode_actions.py --key ABCD1234 START PROBE RESET PROBE
# Actions: IDLE, START, PROBE, RESET, BADPW, GOODPW
# Output: one line per clock cycle
# Format: soft_rst auth_req diag_en pw_valid pw_hex dbg_data_hex
# To save output: python3 encode_actions.py --key ABCD1234 START PROBE RESET PROBE > trial.txt

import argparse

DEMO_PASSWORD = 0xC0DECAFE
# Each public action is (soft_rst, auth_req, diag_en, pw_valid, pw).
# Names may change, but the vectors are the source of truth.
ACTIONS = {
    'IDLE':   (0, 0, 0, 0, 0),
    'START':  (0, 1, 0, 0, 0),
    'PROBE':  (0, 0, 1, 0, 0),
    'RESET':  (1, 0, 0, 0, 0),
    'BADPW':  (0, 0, 0, 1, 0),
    'GOODPW': (0, 0, 0, 1, DEMO_PASSWORD),
}

def vector_for(name, key):
    soft, req, diag, valid, pw = ACTIONS[name]
    return soft, req, diag, valid, pw, key if diag else 0

def format_vector(vector):
    soft, req, diag, valid, pw, key = vector
    return f'{soft} {req} {diag} {valid} {pw:08X} {key:08X}'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key', default='00000000',
                        help='candidate diagnostic input (exactly 8 hex digits)')
    parser.add_argument('actions', nargs='+', choices=sorted(ACTIONS))
    args = parser.parse_args()
    try:
        if len(args.key) != 8:
            raise ValueError('key must be exactly 8 hexadecimal digits')
        key = int(args.key, 16)
    except ValueError as exc:
        parser.error(str(exc))
    for name in args.actions:
        print(format_vector(vector_for(name, key)))

if __name__ == '__main__':
    main()
