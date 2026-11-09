package org.apache.commons.codec.language;

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

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int maxLen = Integer.parseInt(lines.get(0));
        final String[] words = lines.subList(1, lines.size()).toArray(new String[0]);
        final DoubleMetaphone dm = new DoubleMetaphone();
        dm.setMaxCodeLen(maxLen);
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (final String w : words) {
                for (int alt = 0; alt < 2; alt++) {
                    String r;
                    try {
                        r = dm.doubleMetaphone(w, alt == 1);
                    } catch (Throwable t) {
                        r = "!" + t.getClass().getName();
                    }
                    md.update(((r == null ? "<null>" : r) + "\n").getBytes(StandardCharsets.UTF_8));
                }
            }
            System.out.println("{\"cases\":" + (words.length * 2) + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (final String w : words) {
                    final String a = dm.doubleMetaphone(w, false);
                    final String b = dm.doubleMetaphone(w, true);
                    sink += (a == null ? 0 : a.length()) + (b == null ? 0 : b.length());
                }
            }
            final double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + (words.length * 2) + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
