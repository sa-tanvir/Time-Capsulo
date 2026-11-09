package org.jsoup.nodes;

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

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = readLines(size);
        final int n = lines.size();
        final boolean[][] fl = new boolean[n][3];
        final Document.OutputSettings[] os = new Document.OutputSettings[n];
        final String[] str = new String[n];
        final Map<String, Document.OutputSettings> cache = new HashMap<>();
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k).split("\t", -1);
            for (int j = 0; j < 3; j++) fl[k][j] = p[0].charAt(j) == '1';
            final String key = p[1] + "/" + p[2];
            Document.OutputSettings s = cache.get(key);
            if (s == null) {
                s = new Document.OutputSettings().charset(p[1]).escapeMode(Entities.EscapeMode.valueOf(p[2]));
                cache.put(key, s);
            }
            os[k] = s;
            str[k] = unesc(p[3]);
        }
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                final StringBuilder sb = new StringBuilder("#");
                Entities.escape(sb, str[k], os[k], fl[k][0], fl[k][1], fl[k][2]);
                upd(md, sb.toString());
            }
            done(mode, n, 0, md, 0, 0);
        } else {
            long sink = 0;
            final StringBuilder sb = new StringBuilder();
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int k = 0; k < n; k++) {
                    sb.setLength(0);
                    Entities.escape(sb, str[k], os[k], fl[k][0], fl[k][1], fl[k][2]);
                    sink += sb.length();
                }
            }
            done(mode, n, repeat, null, (System.nanoTime() - t0) / 1e9, sink);
        }
    }
}
