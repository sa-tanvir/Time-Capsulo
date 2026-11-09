package org.apache.commons.text;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.List;

public class TCBench {
    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    static TextStringBuilder build(String hay) {
        // spare capacity with stale characters beyond the logical size
        final TextStringBuilder sb = new TextStringBuilder(hay.length() + 16);
        sb.append(hay).append("qqqqqqqq");
        sb.setLength(hay.length());
        return sb;
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final String hay = lines.get(0);
        final int n = lines.size() - 1;
        final int[] st = new int[n];
        final String[] nd = new String[n];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k + 1).split("\t", -1);
            st[k] = Integer.parseInt(p[0]);
            nd[k] = p[1].equals("<null>") ? null : p[1];
        }
        final TextStringBuilder sb = build(hay);
        final TextStringBuilder empty = new TextStringBuilder();
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                md.update((sb.lastIndexOf(nd[k], st[k]) + "," + empty.lastIndexOf(nd[k], st[k]) + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + (2 * n) + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int k = 0; k < n; k++) {
                    sink += sb.lastIndexOf(nd[k], st[k]);
                }
            }
            final double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
