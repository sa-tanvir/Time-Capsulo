package org.apache.commons.codec.net;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.BitSet;
import java.util.List;

public class TCBench {
    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    static byte[] data(int len, long seed) {
        final byte[] d = new byte[len];
        long s = seed * 0x9E3779B97F4A7C15L + 1;
        final String alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:-_!?()/";
        for (int i = 0; i < len; i++) {
            s ^= s << 13;
            s ^= s >>> 7;
            s ^= s << 17;
            final int r = (int) ((s >>> 20) & 0xffff) % 100;
            final int v = (int) ((s >>> 40) & 0xffff);
            if (r < 60) d[i] = (byte) alpha.charAt(v % alpha.length());
            else if (r < 72) d[i] = ' ';
            else if (r < 75) d[i] = '\t';
            else if (r < 78) d[i] = (byte) (v % 2 == 0 ? 13 : 10);
            else if (r < 83) d[i] = '=';
            else d[i] = (byte) v;
        }
        return d;
    }

    static BitSet bits(int kind) {
        if (kind == 0) return null;
        final BitSet b = new BitSet(256);
        if (kind == 1) {
            for (int c = 'a'; c <= 'z'; c++) b.set(c);
            for (int c = 'A'; c <= 'Z'; c++) b.set(c);
            for (int c = '0'; c <= '9'; c++) b.set(c);
        } else {
            for (int c = 33; c <= 126; c++) if (c != '=') b.set(c);
            b.set(' ');
            b.set('\t');
        }
        return b;
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final byte[][] ins = new byte[n][];
        final BitSet[] sets = new BitSet[n];
        final boolean[] strict = new boolean[n];
        for (int i = 0; i < n; i++) {
            final String[] f = lines.get(i).trim().split(" ");
            strict[i] = Integer.parseInt(f[0]) == 1;
            sets[i] = bits(Integer.parseInt(f[1]));
            ins[i] = data(Integer.parseInt(f[2]), Long.parseLong(f[3]));
        }
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int i = 0; i < n; i++) {
                String r;
                try {
                    final byte[] o = QuotedPrintableCodec.encodeQuotedPrintable(sets[i], ins[i], strict[i]);
                    r = hex(o);
                } catch (Throwable t) {
                    r = "!" + t.getClass().getName();
                }
                md.update((r + "\n").getBytes(StandardCharsets.UTF_8));
            }
            final byte[] nul = QuotedPrintableCodec.encodeQuotedPrintable(null, null, true);
            md.update(("null:" + (nul == null) + "\n").getBytes(StandardCharsets.UTF_8));
            System.out.println("{\"cases\":" + (n + 1) + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int i = 0; i < n; i++) {
                    try {
                        sink += QuotedPrintableCodec.encodeQuotedPrintable(sets[i], ins[i], strict[i]).length;
                    } catch (RuntimeException e) {
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
