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
        final DaitchMokotoffSoundex[] encs = { new DaitchMokotoffSoundex(), new DaitchMokotoffSoundex(false) };
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (final DaitchMokotoffSoundex enc : encs) {
                for (final String w : words) {
                    String r1, r2;
                    try {
                        r1 = enc.soundex(w);
                    } catch (Throwable t) {
                        r1 = "!" + t.getClass().getName();
                    }
                    try {
                        r2 = enc.encode(w);
                    } catch (Throwable t) {
                        r2 = "!" + t.getClass().getName();
                    }
                    md.update((r1 + "#" + r2 + "\n").getBytes(StandardCharsets.UTF_8));
                }
                md.update(("<null>" + enc.encode((String) null) + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + (2 * (words.length + 1)) + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (final DaitchMokotoffSoundex enc : encs) {
                    for (final String w : words) {
                        sink += enc.soundex(w).length() + enc.encode(w).length();
                    }
                }
            }
            final double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + (2 * words.length) + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
