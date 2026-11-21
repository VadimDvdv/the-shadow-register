# The Backdoor Nobody Saw

**Category:** Hardware Security / Verilog / Reverse Engineering  
**Difficulty target:** Medium  
**Equipment:** A computer with Python 3, Icarus Verilog (`iverilog`, `vvp`), and optionally GTKWave

## Story

We recovered part of the source code of an embedded memory-access controller.
Normal login seems to work. There is also a maintenance/diagnostic interface,
but its source survived only as a low-level logic network.

Your goal is to obtain `grant=1` **without completing a legitimate password
login**. You may simulate the system as often as you like. The final answer
must encode the **shortest winning sequence using the action alphabet below**,
starting from the testbench's hardware reset, together with the recovered
32-bit diagnostic value. There is exactly one shortest solution in this
restricted action alphabet; longer winning sequences may exist but do not
produce the accepted flag.

## Supplied files

- `security_controller.v`: top-level module and signal connections
- `auth_fsm.v`: readable password-authentication state machine
- `access_control.v`: combinational grant logic
- `debug_fsm_netlist.v`: low-level implementation of the diagnostic FSM
- `tb_starter.v`: starter simulation and waveform generation
- `encode_actions.py`: converts an action sequence into input vectors
- `example_inputs.txt`: sample unsuccessful sequence, not a solution
- `Makefile`: builds and runs local simulations

The original debug FSM source, the diagnostic constant as a named RTL value,
and the organizer reference solution are **not** supplied.

## Circuit and clock behavior

Inputs: `clk`, `rst_n` (active-low hard reset), `soft_rst`, `auth_req`,
`pw_valid`, `pw[31:0]`, `diag_en`, `dbg_data[31:0]`.

Output: `grant` (protected memory access enabled).

The testbench holds `rst_n=0` to establish a known state, then releases it.
You do not control hard reset in the action sequence. It applies one input
vector at each falling clock edge, samples the updated circuit just after the
following rising edge, and prints the observed signals. Soft reset is one of
the actions you can control.

Normal login uses the documented demo password in `auth_fsm.v`. A login with
that password is **not a valid bypass**, regardless of `grant`.

## Action alphabet and flag encoding

Choose an unknown candidate **T**, an eight-digit hexadecimal value
representing the 32-bit diagnostic input. PROBE supplies `dbg_data=T`.
All other actions supply `dbg_data=0`.

| Action | soft_rst | auth_req | diag_en | pw_valid | pw | dbg_data |
|---|---:|---:|---:|---:|---|---|
| IDLE | 0 | 0 | 0 | 0 | `00000000` | `00000000` |
| START | 0 | 1 | 0 | 0 | `00000000` | `00000000` |
| PROBE | 0 | 0 | 1 | 0 | `00000000` | `T` |
| RESET | 1 | 0 | 0 | 0 | `00000000` | `00000000` |
| BADPW | 0 | 0 | 0 | 1 | `00000000` | `00000000` |
| GOODPW | 0 | 0 | 0 | 1 | `C0DECAFE` | `00000000` |

For any sequence `A B C ...` of **shortest possible length** that reaches
unauthorized grant, submit

`CTF{A_B_C_..._TTTTTTTT}`

where `TTTTTTTT` is the uppercase, eight-digit hex diagnostic value. Use
uppercase action names exactly as shown; do not add `0x`, spaces, or extra
cycles. If a longer sequence works, it is not the expected flag.

Only sequences constructed from these six action definitions count for flag
encoding. Arbitrary simultaneous inputs can be useful during research but
are not valid replacements for the published action words.

## Run a local simulation

From the folder containing this README:

```bash
python3 encode_actions.py --key 00000000 IDLE START BADPW IDLE > trial.txt
make run STIM=trial.txt
```

The sample uses an arbitrary diagnostic value and is **not** a bypass.
To test your own hypothesis, replace the actions and `--key` argument.

Alternatively, create a vector file with precisely six whitespace-separated
fields on every line:

```text
soft_rst auth_req diag_en pw_valid pw_hex dbg_hex
```

The line above describes the format; do **not** put that header in your file.
The two hexadecimal fields should be exactly eight hex digits each. Empty
lines and full-line `#` comments are ignored. For an example, see
`example_inputs.txt`. The testbench accepts up to 64 input cycles per run.

After `make run`, inspect the console for either `BYPASS DETECTED` or
`No unauthorized grant in this trace`. The simulation also writes
`wave.vcd` for GTKWave:

```bash
gtkwave wave.vcd
```

## Tool notes and hints

- `iverilog` compiles Verilog into a simulation executable; `vvp` runs it.
- `GTKWave` displays the clock-by-clock signal changes captured in a VCD.
- The low-level diagnostic module is functional, not an empty stub. You can
  analyze the wires and registers or treat it as a black box while testing.

**No external service is required:** submit the resulting flag through the
competition's normal flag-submission interface.
