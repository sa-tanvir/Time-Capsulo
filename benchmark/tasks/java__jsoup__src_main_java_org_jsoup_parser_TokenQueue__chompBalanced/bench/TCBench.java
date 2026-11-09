package org.jsoup.parser;

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

    static String run(TokenQueue tq, char o, char c) {
        String r;
        try {
            r = "OK:" + tq.chompBalanced(o, c);
        } catch (IllegalArgumentException e) {
            r = "ERR:" + e.getMessage();
        }
        return r;
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = readLines(size);
        final int n = lines.size();
        final char[] op = new char[n];
        final char[] cl = new char[n];
        final String[] str = new String[n];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k).split("\t", -1);
            op[k] = unesc(p[0]).charAt(0);
            cl[k] = unesc(p[1]).charAt(0);
            str[k] = unesc(p[2]);
        }
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                final TokenQueue tq = new TokenQueue(str[k]);
                final String r = run(tq, op[k], cl[k]);
                upd(md, r + "|" + tq.remainder());
            }
            done(mode, n, 0, md, 0, 0);
        } else {
            long sink = 0;
            final TokenQueue[] qs = new TokenQueue[n];
            final long[] ns = new long[1];
            for (int rep = 0; rep < repeat; rep++) {
                for (int k = 0; k < n; k++) qs[k] = new TokenQueue(str[k]);
                final long t0 = System.nanoTime();
                for (int k = 0; k < n; k++) sink += run(qs[k], op[k], cl[k]).length();
                ns[0] += System.nanoTime() - t0;
            }
            done(mode, n, repeat, null, ns[0] / 1e9, sink);
        }
    }
}
