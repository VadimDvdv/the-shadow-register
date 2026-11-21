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
