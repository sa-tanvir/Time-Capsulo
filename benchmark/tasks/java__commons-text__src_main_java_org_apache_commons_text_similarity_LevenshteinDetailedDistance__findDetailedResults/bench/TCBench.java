package org.apache.commons.text.similarity;

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

    // Full cost matrix as built by the library: matrix[j][i] = distance(left[0..i), right[0..j)), left is the shorter string
    static int[][] fullMatrix(CharSequence left, CharSequence right) {
        final int n = left.length(), m = right.length();
        final int[][] mx = new int[m + 1][n + 1];
        for (int i = 0; i <= n; i++) mx[0][i] = i;
        for (int j = 0; j <= m; j++) mx[j][0] = j;
        for (int j = 1; j <= m; j++) {
            for (int i = 1; i <= n; i++) {
                if (left.charAt(i - 1) == right.charAt(j - 1)) mx[j][i] = mx[j - 1][i - 1];
                else mx[j][i] = 1 + Math.min(Math.min(mx[j][i - 1], mx[j - 1][i]), mx[j - 1][i - 1]);
            }
        }
        return mx;
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final int inner = size.equals("S") ? 1 : size.equals("M") ? 20 : 150;
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final String[] ls = new String[n], rs = new String[n];
        final int[][][] mats = new int[n][][];
        final boolean[] swapped = new boolean[n];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k).split("\t", -1);
            String l = p[0], r = p[1];
            if (l.length() > r.length()) { final String t = l; l = r; r = t; swapped[k] = true; }
            ls[k] = l; rs[k] = r;
            mats[k] = fullMatrix(l, r);
        }
        final Method mth = LevenshteinDetailedDistance.class.getDeclaredMethod("findDetailedResults",
                CharSequence.class, CharSequence.class, int[][].class, boolean.class);
        mth.setAccessible(true);
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                final Object res = mth.invoke(null, ls[k], rs[k], mats[k], swapped[k]);
                md.update((res + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int q = 0; q < inner; q++) {
                    for (int k = 0; k < n; k++) {
                        final Object res = mth.invoke(null, ls[k], rs[k], mats[k], swapped[k]);
                        sink += ((LevenshteinResults) res).getDistance();
                    }
                }
            }
            final double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
