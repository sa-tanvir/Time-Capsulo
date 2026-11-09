package org.apache.commons.text;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.List;

public class TCBench {
    static final String[] NL = { null, "\n", "<br />", "\r\n" };
    static final String[] ON = { null, "", " ", "/", "[ ,;]+", "-", "\\s", " +", "[,.]" };

    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final int[] wl = new int[n];
        final String[] nl = new String[n], on = new String[n], tx = new String[n];
        final boolean[] lw = new boolean[n];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k).split("\t", 5);
            wl[k] = Integer.parseInt(p[0]);
            nl[k] = NL[Integer.parseInt(p[1])];
            lw[k] = p[2].equals("1");
            on[k] = ON[Integer.parseInt(p[3])];
            tx[k] = p[4];
        }
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                String r;
                try {
                    r = WordUtils.wrap(tx[k], wl[k], nl[k], lw[k], on[k]);
                } catch (Throwable t) {
                    r = "!" + t.getClass().getName();
                }
                md.update((r.replace("\n", "\\n").replace("\r", "\\r") + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int k = 0; k < n; k++) {
                    try {
                        sink += WordUtils.wrap(tx[k], wl[k], nl[k], lw[k], on[k]).length();
                    } catch (Throwable t) {
                        sink += 1;
                    }
                }
            }
            final double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
