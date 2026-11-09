package org.apache.commons.text;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.text.ParsePosition;
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
        final int n = lines.size();
        final int[] st = new int[n];
        final String[] ps = new String[n];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k).split("\t", 2);
            st[k] = Integer.parseInt(p[0]);
            ps[k] = p.length > 1 ? p[1] : "";
        }
        final ExtendedMessageFormat f = new ExtendedMessageFormat("x", java.util.Locale.ROOT);
        final Method m = ExtendedMessageFormat.class.getDeclaredMethod("readArgumentIndex", String.class, ParsePosition.class);
        m.setAccessible(true);
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                final ParsePosition pos = new ParsePosition(st[k]);
                String r;
                try {
                    r = "r" + m.invoke(f, ps[k], pos);
                } catch (InvocationTargetException e) {
                    r = "!" + e.getCause().getClass().getName() + ":" + e.getCause().getMessage();
                }
                md.update((r + "|" + pos.getIndex() + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            long ns = 0;
            for (int rep = 0; rep < repeat; rep++) {
                final ParsePosition[] pp = new ParsePosition[n];
                for (int k = 0; k < n; k++) pp[k] = new ParsePosition(st[k]);
                final long t0 = System.nanoTime();
                for (int k = 0; k < n; k++) {
                    try {
                        sink += (Integer) m.invoke(f, ps[k], pp[k]);
                    } catch (InvocationTargetException e) {
                        sink += 1;
                    }
                }
                ns += System.nanoTime() - t0;
                for (int k = 0; k < n; k++) sink += pp[k].getIndex();
            }
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + (ns / 1e9) + "}");
        }
    }
}
