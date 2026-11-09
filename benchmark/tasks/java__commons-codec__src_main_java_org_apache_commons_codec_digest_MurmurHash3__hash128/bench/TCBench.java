package org.apache.commons.codec.digest;

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

    static byte[] data(int len, long seed) {
        final byte[] d = new byte[len];
        long s = seed * 0x9E3779B97F4A7C15L + 1;
        for (int i = 0; i < len; i++) {
            s ^= s << 13;
            s ^= s >>> 7;
            s ^= s << 17;
            d[i] = (byte) (s >>> 24);
        }
        return d;
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final byte[][] bufs = new byte[n][];
        final int[] lens = new int[n], offs = new int[n], seeds = new int[n];
        for (int i = 0; i < n; i++) {
            final String[] f = lines.get(i).trim().split(" ");
            lens[i] = Integer.parseInt(f[0]);
            offs[i] = Integer.parseInt(f[1]);
            seeds[i] = Integer.parseInt(f[2]);
            bufs[i] = data(offs[i] + lens[i] + 5, Long.parseLong(f[3]));
        }
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int i = 0; i < n; i++) {
                String r;
                try {
                    final long[] h = MurmurHash3.hash128(bufs[i], offs[i], lens[i], seeds[i]);
                    r = h.length + ":" + Long.toHexString(h[0]) + ":" + Long.toHexString(h[1]);
                } catch (Throwable t) {
                    r = "!" + t.getClass().getName();
                }
                md.update((r + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int i = 0; i < n; i++) {
                    final long[] h = MurmurHash3.hash128(bufs[i], offs[i], lens[i], seeds[i]);
                    sink += h[0] ^ h[1];
                }
            }
            final double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
