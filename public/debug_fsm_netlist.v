`timescale 1ns / 1ps
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
    wire w9631;
    wire w3861;
    wire w5602;
    wire w6710;
    wire w2346;
    wire w6529;
    wire w2208;
    wire w1066;
    wire w3960;
    wire w3626;
    wire w6924;
    wire w6742;
    wire w3796;
    wire w3690;
    wire w6964;
    wire w2890;
    wire w5010;
    wire w7701;
    wire w2273;
    wire w8681;
    wire w2291;
    wire w6375;
    wire w3435;
    wire w2506;
    wire w4777;
    wire w4441;
    wire w7070;
    wire w1040;
    wire w6755;
    wire w9535;
    wire w8068;
    wire w1413;
    wire w4561;
    wire w4202;
    wire w3869;
    wire w3169;
    wire w5308;
    wire w7072;
    wire w7123;
    wire w7302;
    reg  q7449;
    reg  q6752;
    reg  q6637;
    assign w6964 = (w3796 & w3690);
    assign w7123 = (q6752 & w5308 & w7072 & diag_en);
    assign w3690 = (w6924 & w6742);
    assign w5010 = ~(pw_valid);
    assign w2346 = (dbg_data[28] & ~dbg_data[2] & dbg_data[12] & dbg_data[9]);
    assign w2506 = (w6375 & w3435);
    assign w2208 = (dbg_data[6] & ~dbg_data[16] & ~dbg_data[10] & dbg_data[25]);
    assign w4561 = ~(auth_fail);
    assign w2273 = (diag_en & auth_check & w5010 & w6964 & w7701);
    assign w3169 = (q7449 & w2890);
    assign w8068 = (w6755 | w9535);
    assign w5602 = ~(~dbg_data[15] | ~dbg_data[31] | dbg_data[27] | dbg_data[7]);
    assign w1413 = (q7449 & w2291);
    assign w1066 = (~dbg_data[14] & dbg_data[17] & ~dbg_data[20] & dbg_data[1]);
    assign w4441 = ~(diag_en);
    assign w6375 = ~(w2890);
    assign w6710 = ~(~dbg_data[0] | ~dbg_data[11] | dbg_data[21] | ~dbg_data[24]);
    assign w3435 = ~(w2273);
    assign w4202 = (q6752 & w4561 & auth_check);
    assign w6924 = (w2346 & w6529);
    assign w6529 = (dbg_data[29] & ~dbg_data[30] & dbg_data[22] & ~dbg_data[8]);
    assign w3960 = (w9631 & w3861);
    assign w3796 = (w3960 & w3626);
    assign w7701 = ~(soft_rst);
    assign w1040 = (auth_fail | w7070);
    assign w7072 = ~(auth_check);
    assign w8681 = ~(w2890);
    assign w3869 = (w1413 | w4202);
    assign w9535 = (q6752 & w1040);
    assign w3861 = ~(dbg_data[19] | ~dbg_data[26] | ~dbg_data[23] | dbg_data[18]);
    assign w7302 = (q6637 | w3169 | w7123);
    assign w6742 = (w2208 & w1066);
    assign w5308 = ~(auth_fail);
    assign w6755 = (q7449 & w2506);
    assign w2291 = (w2273 & w8681);
    assign w3626 = (w5602 & w6710);
    assign w7070 = (w4777 & w4441);
    assign w9631 = (~dbg_data[13] & dbg_data[4] & ~dbg_data[5] & ~dbg_data[3]);
    assign w4777 = ~(auth_check);
    assign w2890 = (diag_en & auth_ok);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            q7449 <= 1'b1;
            q6752 <= 1'b0;
            q6637 <= 1'b0;
        end else begin
            q7449 <= w8068;
            q6752 <= w3869;
            q6637 <= w7302;
        end
    end
    assign dbg_bypass = q6637;
endmodule
