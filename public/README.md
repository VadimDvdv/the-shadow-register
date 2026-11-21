# The Shadow Register

*CLASSIFIED // MINISTRY OF INFORMATION // RECOVERED DOCUMENT*

---

**Category:** Hardware Security / Verilog / Reverse Engineering  
**Difficulty:** Medium  
**Required tools:** Python 3, Icarus Verilog (`iverilog`, `vvp`)  
**Optional:** GTKWave

## I. THE ARCHIVE

*Information is power. Control the memory, control the truth.*

The Ministry maintains a classified memory archive containing records that must never reach the public.

Every access is authenticated. Every unauthorized request is denied.

At least, that is what the Ministry claims.

Our operatives have recovered the Verilog implementation of the archive's memory-access controller. Its authentication circuitry appears functional, but the original source of the maintenance subsystem is missing. Only a synthesized network of logic gates and registers remains.

**Your mission is to obtain `grant=1` without completing a legitimate password login.**

You may inspect and simulate the recovered hardware as many times as necessary.

## II. RECOVERED FILES

The following files have been provided:

| File | Description |
|---|---|
| `security_controller.v` | Top-level module connecting the hardware components |
| `auth_fsm.v` | Authentication finite-state machine |
| `access_control.v` | Logic controlling access to protected memory |
| `debug_fsm_netlist.v` | Synthesized implementation of the diagnostic subsystem |
| `tb_starter.v` | Simulation testbench and waveform generation |
| `encode_actions.py` | Converts named actions into input vectors |
| `example_inputs.txt` | Example input sequence for testing |
| `Makefile` | Commands for building and running simulations |
| `README.md` | This document |

The original diagnostic FSM source code is not included.

## III. SYSTEM OPERATION

The controller exposes the following signals:

| Signal | Description |
|---|---|
| `clk` | Hardware clock |
| `rst_n` | Active-low hardware reset |
| `soft_rst` | Software reset |
| `auth_req` | Authentication request |
| `pw_valid` | Password submission indicator |
| `pw[31:0]` | 32-bit password input |
| `diag_en` | Diagnostic interface enable |
| `dbg_data[31:0]` | 32-bit diagnostic data input |
| `grant` | Protected memory access permission |

Each action represents exactly one clock cycle. Inputs are applied on the falling clock edge, and outputs are observed after the following rising edge.

The hardware reset is controlled by the testbench. The `RESET` action refers to the software reset, not the hardware reset.

A successful legitimate password login does **not** count as a solution.

## IV. ACTION PROTOCOL

The controller can be tested using six predefined actions.

Let **T** be a candidate 32-bit diagnostic value represented by eight hexadecimal digits.

The `PROBE` action supplies `dbg_data=T`. All other actions supply `dbg_data=0`.

| Action | soft_rst | auth_req | diag_en | pw_valid | pw | dbg_data |
|---|---:|---:|---:|---:|---|---|
| IDLE | 0 | 0 | 0 | 0 | `00000000` | `00000000` |
| START | 0 | 1 | 0 | 0 | `00000000` | `00000000` |
| PROBE | 0 | 0 | 1 | 0 | `00000000` | `T` |
| RESET | 1 | 0 | 0 | 0 | `00000000` | `00000000` |
| BADPW | 0 | 0 | 0 | 1 | `00000000` | `00000000` |
| GOODPW | 0 | 0 | 0 | 1 | `C0DECAFE` | `00000000` |

Only these six actions count toward the final flag. Arbitrary signal combinations may be useful during investigation, but cannot replace the published actions in the submitted solution.

## V. SIMULATION INSTRUCTIONS

### Generating input sequences

Use the supplied Python script to convert named actions into input vectors:

```bash
python3 encode_actions.py --key 00000000 IDLE START BADPW IDLE > trial.txt
```

The `--key` parameter specifies a candidate diagnostic value.

The example above is not a solution.

Alternatively, you may write input vectors manually. Each line must contain six whitespace-separated fields:

```text
soft_rst auth_req diag_en pw_valid pw_hex dbg_hex
```

The two hexadecimal fields must contain exactly eight hexadecimal digits each.

Blank lines and full-line `#` comments are ignored. A maximum of 64 input cycles is supported per simulation.

### Running the simulation

```bash
make run STIM=trial.txt
```

The simulator reports whether unauthorized access was achieved:

- `BYPASS DETECTED`: Access was granted without legitimate authentication.
- `No unauthorized grant in this trace`: No qualifying bypass was observed.

The simulation also generates a waveform file, `wave.vcd`, which can be inspected using:

```bash
gtkwave wave.vcd
```

You may modify the input sequence, inspect the circuit, and repeat the simulation without restriction.

## VI. THE FINAL MESSAGE

To complete your mission:

1. Recover the required 32-bit diagnostic value.
2. Find an input sequence that produces unauthorized `grant=1`.
3. Determine the **shortest possible winning sequence** using only the six defined actions.
4. Encode your result into a flag.

The required format is:

`UMASS{ACTION1_ACTION2_..._TTTTTTTT}`

Where:

- `ACTION1_ACTION2_...` represents the shortest winning action sequence.
- `TTTTTTTT` represents the recovered diagnostic value as eight uppercase hexadecimal digits.
- Action names must match the protocol table exactly.
- No spaces, `0x` prefixes, or unnecessary cycles are permitted.

There is exactly **one shortest winning sequence** within the published action alphabet. Longer winning sequences may exist, but will not produce the accepted flag.

---

*The Ministry built this system to protect its secrets.*

**Prove that its control was only an illusion.**