package org.apache.commons.lang3;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.*;

public class TCBench {

    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    static String u(String s) {
        if (s.equals("<null>")) return null;
        if (s.indexOf('\\') < 0) return s;
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\\' && i + 1 < s.length()) {
                char nx = s.charAt(++i);
                sb.append(nx == 't' ? '\t' : nx == 'n' ? '\n' : nx == 'r' ? '\r' : nx);
            } else sb.append(c);
        }
        return sb.toString();
    }

    static String rep(String s, int n) {
        if (s == null || n == 1) return s;
        StringBuilder sb = new StringBuilder(s.length() * n);
        for (int i = 0; i < n; i++) sb.append(s);
        return sb.toString();
    }

    static String err(Throwable t) {
        if (t instanceof java.lang.reflect.InvocationTargetException) t = t.getCause();
        return "!" + t.getClass().getName() + ":" + t.getMessage();
    }

    static String call(int k) {
        try {
            return doCall(k);
        } catch (Throwable t) {
            return err(t);
        }
    }

    static String[] text; static String[][] search, repl; static boolean[] rpt; static int[] ttl;
    static java.lang.reflect.Method m;
    static String[] arr(String f) {
        if (f.equals("<null>")) return null;
        if (f.length() == 1) return new String[0];
        String[] parts = f.substring(1).split("\u001f", -1);
        String[] r = new String[parts.length];
        for (int i = 0; i < r.length; i++) r[i] = parts[i].charAt(0) == 'N' ? null : u(parts[i].substring(1));
        return r;
    }

    static String doCall(int k) throws Throwable {
        return String.valueOf(m.invoke(null, text[k], search[k], repl[k], rpt[k], ttl[k]));
    }

    static long fast(int k) throws Throwable {
        return call(k).length();
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        text = new String[n]; search = new String[n][]; repl = new String[n][]; rpt = new boolean[n]; ttl = new int[n];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k).split("\t", -1);
            text[k] = rep(u(p[0]), Integer.parseInt(p[1]));
            search[k] = arr(p[2]); repl[k] = arr(p[3]);
            rpt[k] = p[4].equals("1"); ttl[k] = Integer.parseInt(p[5]);
        }
        m = StringUtils.class.getDeclaredMethod("replaceEach", String.class, String[].class, String[].class, boolean.class, int.class);
        m.setAccessible(true);
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                md.update((call(k) + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            double el = 0;
            for (int rep = 0; rep < repeat; rep++) {
                
                final long t0 = System.nanoTime();
                for (int k = 0; k < n; k++) {
                    try {
                        sink += fast(k);
                    } catch (Throwable t) {
                        sink += 1;
                    }
                }
                el += (System.nanoTime() - t0) / 1e9;
            }
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
