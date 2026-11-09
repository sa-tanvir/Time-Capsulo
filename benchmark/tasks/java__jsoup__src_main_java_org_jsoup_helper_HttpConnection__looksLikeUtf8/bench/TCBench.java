package org.jsoup.helper;

import java.lang.reflect.Method;

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

    static byte[] unhex(String s) {
        final byte[] b = new byte[s.length() / 2];
        for (int i = 0; i < b.length; i++) b[i] = (byte) Integer.parseInt(s.substring(2 * i, 2 * i + 2), 16);
        return b;
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = readLines(size);
        final int n = lines.size();
        final byte[][] in = new byte[n][];
        for (int k = 0; k < n; k++) in[k] = unhex(lines.get(k).split("\t", -1)[1]);
        final Method m = Class.forName("org.jsoup.helper.HttpConnection$Base").getDeclaredMethod("looksLikeUtf8", byte[].class);
        m.setAccessible(true);
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            final StringBuilder sb = new StringBuilder();
            for (int k = 0; k < n; k++) sb.append(((Boolean) m.invoke(null, (Object) in[k])) ? '1' : '0');
            upd(md, sb.toString());
            done(mode, n, 0, md, 0, 0);
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int k = 0; k < n; k++) if ((Boolean) m.invoke(null, (Object) in[k])) sink++;
            }
            done(mode, n, repeat, null, (System.nanoTime() - t0) / 1e9, sink);
        }
    }
}
