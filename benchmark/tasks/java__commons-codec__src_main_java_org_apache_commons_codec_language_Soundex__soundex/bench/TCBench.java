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
        final String[] words = lines.toArray(new String[0]);
        final Soundex[] encs = { Soundex.US_ENGLISH, Soundex.US_ENGLISH_SIMPLIFIED, Soundex.US_ENGLISH_GENEALOGY };
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (final Soundex enc : encs) {
                for (final String w : words) {
                    String r;
                    try {
                        r = enc.soundex(w);
                    } catch (Throwable t) {
                        r = "!" + t.getClass().getName();
                    }
                    md.update(((r == null ? "<null>" : r) + "\n").getBytes(StandardCharsets.UTF_8));
                }
                md.update(("<null-in>" + enc.soundex(null) + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + (3 * (words.length + 1)) + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (final Soundex enc : encs) {
                    for (final String w : words) {
                        try {
                            sink += enc.soundex(w).length();
                        } catch (IllegalArgumentException e) {
                            sink += 1;
                        }
                    }
                }
            }
            final double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + (3 * words.length) + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
