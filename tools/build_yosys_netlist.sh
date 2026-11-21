#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v yosys >/dev/null || { echo 'yosys not installed' >&2; exit 127; }
# After synthesis, remove attributes and replace non-port identifiers.
# Regenerate the public netlist and rerun make check before release.
yosys -Q -T -p '
  read_verilog private/debug_fsm.v
  synth -top debug_fsm
  opt_clean -purge
  rename -hide
  rename -enumerate
  write_verilog -noattr public/debug_fsm_netlist.v
'
