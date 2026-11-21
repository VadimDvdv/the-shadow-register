`timescale 1ns/1ps
// Input vectors: soft_rst auth_req diag_en pw_valid pw_hex dbg_hex
// Each valid vector is driven at a negedge and sampled after the next posedge.
module tb_starter;
    reg clk = 1'b0;
    reg rst_n, soft_rst, auth_req, diag_en, pw_valid;
    reg [31:0] pw, dbg_data;
    wire grant;
    reg [1023:0] stimulus_path;
    reg [2047:0] line;
    integer fd, got, fields, cycle, s, a, d, v;
    reg [31:0] p, key;
    reg auth_seen, bypass_seen;

    security_controller dut (
        .clk(clk), .rst_n(rst_n), .soft_rst(soft_rst),
        .auth_req(auth_req), .pw_valid(pw_valid), .pw(pw),
        .diag_en(diag_en), .dbg_data(dbg_data), .grant(grant)
    );
    always #5 clk = ~clk;

    // $sscanf may report zero fields for an invalid first token. Only
    // whitespace-only lines and lines beginning with # may be skipped.
    function is_ignorable;
        input [2047:0] source_line;
        integer n;
        reg [7:0] ch;
        reg seen_first;
        begin
            is_ignorable = 1'b1;
            seen_first = 1'b0;
            for (n = 255; n >= 0; n = n - 1) begin
                ch = source_line[n*8 +: 8];
                if (!seen_first && ch != 8'h00 && ch != 8'h20 &&
                    ch != 8'h09 && ch != 8'h0A && ch != 8'h0D) begin
                    seen_first = 1'b1;
                    if (ch != 8'h23) is_ignorable = 1'b0; // #
                end
            end
        end
    endfunction

    initial begin
        rst_n = 0; soft_rst = 0; auth_req = 0; pw_valid = 0;
        pw = 0; diag_en = 0; dbg_data = 0;
        auth_seen = 0; bypass_seen = 0; cycle = 0;
        if (!$value$plusargs("STIM=%s", stimulus_path))
            $fatal(1, "Provide +STIM=path/to/inputs.txt");
        fd = $fopen(stimulus_path, "r");
        if (fd == 0) $fatal(1, "Could not open stimulus file");
        $dumpfile("wave.vcd");
        $dumpvars(0, tb_starter);

        // Hard reset initializes both FSMs before any participant input.
        repeat (2) @(negedge clk);
        rst_n = 1;

        // Do not stop at cycle 64; read through EOF to distinguish exactly
        // 64 cycles (valid) from 65+ cycles (invalid).
        while (!$feof(fd)) begin
            line = 0;
            got = $fgets(line, fd);
            if (got != 0) begin
                fields = $sscanf(line, "%d %d %d %d %h %h", s, a, d, v, p, key);
                if (fields == 6) begin
                    if (cycle >= 64)
                        $fatal(1, "Input exceeds 64 cycles");
                    // Case inequality and reduction XOR reject unknown Z/X
                    // rather than relying on comparisons that evaluate to X.
                    if ((s !== 0 && s !== 1) ||
                        (a !== 0 && a !== 1) ||
                        (d !== 0 && d !== 1) ||
                        (v !== 0 && v !== 1) ||
                        (^{p, key} === 1'bx))
                        $fatal(1, "Controls must be 0/1 and hex fields must not contain x/z");

                    soft_rst = s;
                    auth_req = a;
                    diag_en = d;
                    pw_valid = v;
                    pw = p;
                    dbg_data = key;
                    @(posedge clk);
                    #1; // nonblocking sequential assignments have settled
                    cycle = cycle + 1;
                    if (dut.auth_ok) auth_seen = 1;
                    $display("cycle=%0d CHECK=%b AUTH=%b FAIL=%b DEBUG=%b GRANT=%b",
                        cycle, dut.auth_check, dut.auth_ok, dut.auth_fail,
                        dut.dbg_bypass, grant);
                    if (grant && !auth_seen) bypass_seen = 1;
                    @(negedge clk);
                end else if (!is_ignorable(line)) begin
                    $fatal(1, "Malformed line after cycle %0d", cycle);
                end
                // Blank or # comment lines are ignored, without using cycles.
            end
        end
        $fclose(fd);
        if (bypass_seen)
            $display("BYPASS DETECTED: grant without successful authentication");
        else
            $display("No unauthorized grant in this trace");
        $finish;
    end
endmodule
