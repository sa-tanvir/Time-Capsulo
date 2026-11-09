package org.apache.commons.text.similarity;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
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

    static String call(Method m, CharSequence a, CharSequence b, int t) throws Exception {
        try {
            return String.valueOf(m.invoke(null, a, b, t));
        } catch (InvocationTargetException e) {
            return "!" + e.getCause().getClass().getName() + ":" + e.getCause().getMessage();
        }
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final String[] ls = new String[n], rs = new String[n];
        final int[] ts = new int[n];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k).split("\t", -1);
            ls[k] = p[0].equals("<null>") ? null : p[0];
            rs[k] = p[1].equals("<null>") ? null : p[1];
            ts[k] = Integer.parseInt(p[2]);
        }
        final Method mth = LevenshteinDistance.class.getDeclaredMethod("limitedCompare", CharSequence.class, CharSequence.class, int.class);
        mth.setAccessible(true);
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                md.update((call(mth, ls[k], rs[k], ts[k]) + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int k = 0; k < n; k++) {
                    try {
                        sink += String.valueOf(mth.invoke(null, ls[k], rs[k], ts[k])).length();
                    } catch (InvocationTargetException e) {
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
