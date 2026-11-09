package org.apache.commons.text.translate;

import java.io.StringWriter;
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
        final String[] in = lines.toArray(new String[0]);
        final NumericEntityUnescaper[] cfg = {
            new NumericEntityUnescaper(),
            new NumericEntityUnescaper(NumericEntityUnescaper.OPTION.semiColonOptional),
            new NumericEntityUnescaper(NumericEntityUnescaper.OPTION.errorIfNoSemiColon),
            new NumericEntityUnescaper(NumericEntityUnescaper.OPTION.semiColonRequired, NumericEntityUnescaper.OPTION.errorIfNoSemiColon)
        };
        long cases = 0;
        for (String s : in) cases += (long) s.length() * cfg.length;
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (final NumericEntityUnescaper u : cfg) {
                for (final String s : in) {
                    final StringBuilder sb = new StringBuilder();
                    final StringWriter w = new StringWriter();
                    for (int i = 0; i < s.length(); i++) {
                        w.getBuffer().setLength(0);
                        String r;
                        try {
                            r = Integer.toString(u.translate(s, i, w));
                        } catch (Throwable t) {
                            r = "!" + t.getClass().getName();
                        }
                        final String o = w.toString();
                        if (!r.equals("0") || !o.isEmpty()) {
                            sb.append(i).append(':').append(r).append(':');
                            for (int q = 0; q < o.length(); q++) sb.append((int) o.charAt(q)).append(',');
                            sb.append(';');
                        }
                    }
                    md.update((sb + "\n").getBytes(StandardCharsets.UTF_8));
                }
            }
            System.out.println("{\"cases\":" + cases + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final StringWriter w = new StringWriter();
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (final NumericEntityUnescaper u : cfg) {
                    for (final String s : in) {
                        w.getBuffer().setLength(0);
                        for (int i = 0; i < s.length(); i++) {
                            try {
                                sink += u.translate(s, i, w);
                            } catch (Throwable t) {
                                sink += 1;
                            }
                        }
                        sink += w.getBuffer().length();
                    }
                }
            }
            final double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + cases + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
