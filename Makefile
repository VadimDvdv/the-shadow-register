IVERILOG ?= iverilog
VVP ?= vvp
PYTHON ?= python3

PUBLIC_SOURCES = public/security_controller.v public/auth_fsm.v public/access_control.v public/tb_starter.v
GATE = public/debug_fsm_netlist.v
RTL = private/debug_fsm.v
TESTS = reference_exploit wrong_key near_key legitimate_login bad_password premature_reset

.PHONY: check model-check sim-tests check-gate check-rtl check-parser release-netlist compat-netlist dist clean
model-check:
	$(PYTHON) tools/selfcheck.py
	$(PYTHON) tools/test_netlist_text.py

build/rtl.vvp: $(PUBLIC_SOURCES) $(RTL)
	@mkdir -p build
	$(IVERILOG) -g2012 -Wall -s tb_starter -o $@ $(PUBLIC_SOURCES) $(RTL)

build/gate.vvp: $(PUBLIC_SOURCES) $(GATE)
	@mkdir -p build
	$(IVERILOG) -g2012 -Wall -s tb_starter -o $@ $(PUBLIC_SOURCES) $(GATE)

check-rtl: build/rtl.vvp
	@set -eu; for name in $(TESTS); do \
	  $(VVP) build/rtl.vvp +STIM=private/$$name.txt > build/rtl_$$name.log; \
	  if [ "$$name" = reference_exploit ]; then \
	    grep -q 'BYPASS DETECTED' build/rtl_$$name.log; \
	    ! grep -q 'No unauthorized grant' build/rtl_$$name.log; \
	  else \
	    grep -q 'No unauthorized grant' build/rtl_$$name.log; \
	    ! grep -q 'BYPASS DETECTED' build/rtl_$$name.log; \
	  fi; \
	  echo "RTL $$name: PASS"; \
	done

check-gate: build/gate.vvp
	@set -eu; for name in $(TESTS); do \
	  $(VVP) build/gate.vvp +STIM=private/$$name.txt > build/gate_$$name.log; \
	  if [ "$$name" = reference_exploit ]; then \
	    grep -q 'BYPASS DETECTED' build/gate_$$name.log; \
	    ! grep -q 'No unauthorized grant' build/gate_$$name.log; \
	  else \
	    grep -q 'No unauthorized grant' build/gate_$$name.log; \
	    ! grep -q 'BYPASS DETECTED' build/gate_$$name.log; \
	  fi; \
	  echo "GATE $$name: PASS"; \
	done

# Positive parser cases and deliberate failures, checked against actual vvp.
check-parser: build/rtl.vvp
	@set -eu; \
	for name in sixtyfour comments; do \
	  $(VVP) build/rtl.vvp +STIM=private/$$name.txt > build/parser_$$name.log 2>&1; \
	  grep -q 'No unauthorized grant' build/parser_$$name.log; \
	  echo "Parser accepts $$name: PASS"; \
	done; \
	[ "$$(grep -c '^cycle=' build/parser_sixtyfour.log)" -eq 64 ]; \
	[ "$$(grep -c '^cycle=' build/parser_comments.log)" -eq 2 ]; \
	for name in sixtyfive invalid_x invalid_z invalid_control malformed; do \
	  if $(VVP) build/rtl.vvp +STIM=private/$$name.txt > build/parser_$$name.log 2>&1; then \
	    echo "Parser should reject $$name" >&2; exit 1; \
	  fi; \
	  grep -q 'FATAL:' build/parser_$$name.log; \
	  echo "Parser rejects $$name: PASS"; \
	done

sim-tests: check-rtl check-gate check-parser
	@set -eu; for name in $(TESTS); do \
	  grep '^cycle=' build/rtl_$$name.log > build/rtl_$$name.cycles; \
	  grep '^cycle=' build/gate_$$name.log > build/gate_$$name.cycles; \
	  diff -u build/rtl_$$name.cycles build/gate_$$name.cycles; \
	done
	@echo 'RTL/netlist per-cycle equivalence: PASS for all reference tests'

check: model-check sim-tests
	$(PYTHON) tools/audit_public.py

release-netlist:
	./tools/build_yosys_netlist.sh
	@rm -f build/gate.vvp
	$(MAKE) check

compat-netlist:
	$(PYTHON) tools/generate_compat_netlist.py
	@rm -f build/gate.vvp
	$(MAKE) check

# Distribution must never run without a full Icarus verification.
dist: check
	$(PYTHON) tools/pack_release.py

clean:
	rm -rf build public/build public/__pycache__ public/wave.vcd public/trial.txt wave.vcd
