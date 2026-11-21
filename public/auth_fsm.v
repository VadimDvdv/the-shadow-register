`timescale 1ns / 1ps

module auth_fsm (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        soft_rst,
    input  wire        auth_req,
    input  wire        pw_valid,
    input  wire [31:0] pw,
    output wire        auth_check,
    output wire        auth_ok,
    output wire        auth_fail
);
    // Public demo password. Successfully using it does NOT solve the challenge.
    localparam [31:0] DEMO_PASSWORD = 32'hC0DECAFE;
    localparam [1:0] S_IDLE = 2'd0, S_CHECK = 2'd1, S_OK = 2'd2;
    reg [1:0] state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) state <= S_IDLE;
        else if (soft_rst) state <= S_IDLE;
        else begin
            case (state)
                S_IDLE:  if (auth_req) state <= S_CHECK;
                S_CHECK: if (pw_valid)
                             state <= (pw == DEMO_PASSWORD) ? S_OK : S_IDLE;
                S_OK:    state <= S_OK;
                default: state <= S_IDLE;
            endcase
        end
    end

    assign auth_check = (state == S_CHECK);
    assign auth_ok    = (state == S_OK);
    // A pulse for a completed, rejected password attempt only.
    // If soft reset has priority, no password is actually checked that cycle.
    assign auth_fail  = (state == S_CHECK) && pw_valid && (pw != DEMO_PASSWORD) && !soft_rst;
endmodule
