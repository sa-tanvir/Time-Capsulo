package org.jsoup.parser;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.reflect.Method;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.*;


public class TCBench {
    static final MethodHandle MH;
    static {
        try {
            final Method m = CharacterReader.class.getDeclaredMethod("cacheString", char[].class, String[].class, int.class, int.class);
            m.setAccessible(true);
            MH = MethodHandles.lookup().unreflect(m);
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    static String unesc(String s) {
        if (s.indexOf('\\') < 0) return s;
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c != '\\') { b.append(c); continue; }
            char d = s.charAt(++i);
            switch (d) {
                case 't': b.append('\t'); break;
                case 'n': b.append('\n'); break;
                case 'f': b.append('\f'); break;
                case 'r': b.append('\r'); break;
                case '\\': b.append('\\'); break;
                case 'u': b.append((char) Integer.parseInt(s.substring(i + 1, i + 5), 16)); i += 4; break;
                default: throw new IllegalStateException("bad escape");
            }
        }
        return b.toString();
    }

    static List<String> readLines(String size) throws Exception {
        return Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
    }

    static void upd(MessageDigest md, String s) {
        md.update(s.getBytes(StandardCharsets.UTF_8));
        md.update((byte) 10);
    }

    static void done(String mode, int cases, int repeat, MessageDigest md, double el, long sink) {
        if (mode.equals("check")) {
            System.out.println("{\"cases\":" + cases + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + cases + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }

    public static void main(String[] args) throws Throwable {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = readLines(size);
        final char[] buf = unesc(lines.get(0)).toCharArray();
        final int n = lines.size() - 1;
        final int[] st = new int[n], ct = new int[n], rp = new int[n];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k + 1).split("\t", -1);
            st[k] = Integer.parseInt(p[0]);
            ct[k] = Integer.parseInt(p[1]);
            rp[k] = Integer.parseInt(p[2]);
        }
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            final String[] cache = new String[512];
            final StringBuilder sb = new StringBuilder();
            for (int k = 0; k < n; k++) {
                final String a = (String) MH.invokeExact(buf, cache, st[k], ct[k]);
                sb.append(a).append(',');
                if (rp[k] == 2) {
                    final String b = (String) MH.invokeExact(buf, cache, st[k], ct[k]);
                    sb.append(a.equals(b) ? (a == b ? "S" : "D") : "X").append(',');
                }
                if (sb.length() > 100000) { upd(md, sb.toString()); sb.setLength(0); }
            }
            upd(md, sb.toString());
            done(mode, n, 0, md, 0, 0);
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                final String[] cache = new String[512];
                for (int k = 0; k < n; k++) {
                    final String a = (String) MH.invokeExact(buf, cache, st[k], ct[k]);
                    sink += a.length();
                    if (rp[k] == 2) {
                        final String b = (String) MH.invokeExact(buf, cache, st[k], ct[k]);
                        if (a == b) sink++;
                    }
                }
            }
            done(mode, n, repeat, null, (System.nanoTime() - t0) / 1e9, sink);
        }
    }
}
