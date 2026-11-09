package org.apache.commons.text.diff;

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

    static String fmt(Object snake) throws Exception {
        if (snake == null) return "null";
        final Class<?> c = snake.getClass();
        final Method[] g = { c.getDeclaredMethod("getStart"), c.getDeclaredMethod("getEnd"), c.getDeclaredMethod("getDiag") };
        final StringBuilder sb = new StringBuilder();
        for (Method m : g) { m.setAccessible(true); sb.append(m.invoke(snake)).append(','); }
        return sb.toString();
    }

    static String run(Method m, StringsComparator c, int[] r) throws Exception {
        try {
            return fmt(m.invoke(c, r[0], r[1], r[2], r[3]));
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
        final int[][] ranges = new int[n][4];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k).split("\t", -1);
            ls[k] = p[0]; rs[k] = p[1];
            for (int q = 0; q < 4; q++) ranges[k][q] = Integer.parseInt(p[2 + q]);
        }
        final Method mth = StringsComparator.class.getDeclaredMethod("getMiddleSnake", int.class, int.class, int.class, int.class);
        mth.setAccessible(true);
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                md.update((run(mth, new StringsComparator(ls[k], rs[k]), ranges[k]) + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            long ns = 0;
            for (int rep = 0; rep < repeat; rep++) {
                final StringsComparator[] cs = new StringsComparator[n];
                for (int k = 0; k < n; k++) cs[k] = new StringsComparator(ls[k], rs[k]);
                final long t0 = System.nanoTime();
                for (int k = 0; k < n; k++) {
                    try {
                        final Object o = mth.invoke(cs[k], ranges[k][0], ranges[k][1], ranges[k][2], ranges[k][3]);
                        sink += o == null ? 1 : System.identityHashCode(o) & 1;
                    } catch (InvocationTargetException e) {
                        sink += 2;
                    }
                }
                ns += System.nanoTime() - t0;
            }
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + (ns / 1e9) + "}");
        }
    }
}
