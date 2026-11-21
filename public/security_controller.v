`timescale 1ns/1ps
// Public: complete top-level connections. Debug source is distributed as gates.
module security_controller (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        soft_rst,
    input  wire        auth_req,
    input  wire        pw_valid,
    input  wire [31:0] pw,
    input  wire        diag_en,
    input  wire [31:0] dbg_data,
    output wire        grant
);
    wire auth_check;
    wire auth_ok;
    wire auth_fail;
    wire dbg_bypass;

    auth_fsm u_auth (
        .clk(clk), .rst_n(rst_n), .soft_rst(soft_rst),
        .auth_req(auth_req), .pw_valid(pw_valid), .pw(pw),
        .auth_check(auth_check), .auth_ok(auth_ok), .auth_fail(auth_fail)
    );

    debug_fsm u_debug (
        .clk(clk), .rst_n(rst_n), .soft_rst(soft_rst),
        .diag_en(diag_en), .dbg_data(dbg_data),
        .auth_check(auth_check), .auth_ok(auth_ok),
        .auth_fail(auth_fail), .pw_valid(pw_valid),
        .dbg_bypass(dbg_bypass)
    );

    access_control u_access (
        .auth_ok(auth_ok), .dbg_bypass(dbg_bypass), .grant(grant)
    );
endmodule
