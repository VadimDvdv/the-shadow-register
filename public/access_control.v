`timescale 1ns / 1ps

module access_control (
    input  wire auth_ok,
    input  wire dbg_bypass,
    output wire grant
);
    assign grant = auth_ok | dbg_bypass;
endmodule
