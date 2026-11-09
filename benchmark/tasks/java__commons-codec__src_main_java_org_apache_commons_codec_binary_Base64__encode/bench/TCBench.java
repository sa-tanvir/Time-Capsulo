package org.apache.commons.codec.binary;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.Arrays;
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

    static final class Case {
        int lineLength, variant, chunk;
        byte[] sep, data;
        Base64 codec;
    }

    static BaseNCodec.Context run(final Case c, final boolean extra) {
        final BaseNCodec.Context ctx = new BaseNCodec.Context();
        final byte[] d = c.data;
        if (c.chunk <= 0) {
            c.codec.encode(d, 0, d.length, ctx);
        } else {
            int pos = 0;
            while (pos < d.length) {
                final int n = Math.min(c.chunk, d.length - pos);
                c.codec.encode(d, pos, n, ctx);
                pos += n;
            }
        }
        c.codec.encode(null, 0, -1, ctx);
        if (extra) {
            // further calls after end of input must have no effect
            c.codec.encode(d, 0, Math.min(5, d.length), ctx);
            c.codec.encode(null, 0, -1, ctx);
        }
        return ctx;
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final Case[] cases = new Case[lines.size()];
        for (int i = 0; i < cases.length; i++) {
            final String[] f = lines.get(i).trim().split(" ");
            final Case c = new Case();
            c.lineLength = Integer.parseInt(f[0]);
            c.variant = Integer.parseInt(f[1]);
            c.sep = Integer.parseInt(f[2]) == 0 ? new byte[] {13, 10} : new byte[] {10};
            c.chunk = Integer.parseInt(f[3]);
            c.data = data(Integer.parseInt(f[4]), Long.parseLong(f[5]));
            c.codec = new Base64(c.lineLength, c.sep, c.variant == 1);
            cases[i] = c;
        }
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int i = 0; i < cases.length; i++) {
                final Case c = cases[i];
                String r;
                try {
                    final BaseNCodec.Context ctx = run(c, i % 2 == 0);
                    r = (ctx.buffer == null ? "<nobuf>" : hex(Arrays.copyOf(ctx.buffer, ctx.pos)))
                        + "|" + ctx.pos + "|" + ctx.modulus + "|" + ctx.currentLinePos + "|" + ctx.eof + "|" + ctx.readPos;
                } catch (Throwable t) {
                    r = "!" + t.getClass().getName();
                }
                md.update((r + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + cases.length + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (final Case c : cases) {
                    final BaseNCodec.Context ctx = run(c, false);
                    sink += ctx.pos + (ctx.buffer == null ? 0 : ctx.buffer[ctx.pos > 0 ? ctx.pos - 1 : 0]);
                }
            }
            final double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + cases.length + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
