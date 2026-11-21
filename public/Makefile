IVERILOG ?= iverilog
VVP ?= vvp
STIM ?= example_inputs.txt

SOURCES = security_controller.v auth_fsm.v access_control.v debug_fsm_netlist.v tb_starter.v

.PHONY: run clean
build/local.vvp: $(SOURCES)
	@mkdir -p build
	$(IVERILOG) -g2012 -s tb_starter -Wall -o $@ $(SOURCES)
run: build/local.vvp
	$(VVP) build/local.vvp +STIM=$(STIM)
clean:
	rm -rf build wave.vcd trial.txt
