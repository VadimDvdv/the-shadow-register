`timescale 1ns/1ps
// ORGANIZER ONLY. Never distribute this human-readable RTL.
module debug_fsm (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        soft_rst,
    input  wire        diag_en,
    input  wire [31:0] dbg_data,
    input  wire        auth_check,
    input  wire        auth_ok,
    input  wire        auth_fail,
    input  wire        pw_valid,
    output wire        dbg_bypass
);
    localparam [31:0] DBG_KEY = 32'hB7C29A53;
    localparam [1:0] D_LOCKED = 2'd0, D_ARMED = 2'd1, D_ACTIVE = 2'd2;
    reg [1:0] state;
    wire key_ok = (dbg_data == DBG_KEY);

    // Diagnostic requests are intended to proceed only after authorization.
    // A hard reset (rst_n) clears diagnostic privilege. A soft reset does not.
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= D_LOCKED;
        else begin
            case (state)
                D_LOCKED: begin
                    if (diag_en && auth_ok)
                        state <= D_ACTIVE;
                    else if (diag_en && auth_check && !pw_valid &&
                             key_ok && !soft_rst)
                        state <= D_ARMED;
                end

                D_ARMED: begin
                    if (auth_fail)
                        state <= D_LOCKED;
                    else if (!auth_check)
                        state <= diag_en ? D_ACTIVE : D_LOCKED;
                    // BUG: assumes CHECK ended without rejection => authorized.
                    // soft_rst also ends CHECK but never produces auth_fail.
                end

                D_ACTIVE: state <= D_ACTIVE;
                default:  state <= D_LOCKED;
            endcase
        end
    end

    assign dbg_bypass = (state == D_ACTIVE);
endmodule
