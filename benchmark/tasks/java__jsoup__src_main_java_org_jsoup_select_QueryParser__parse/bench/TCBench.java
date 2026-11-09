package org.jsoup.select;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;

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

    static String parse(String q) {
        try {
            return QueryParser.parse(q).toString();
        } catch (RuntimeException e) {
            return "ERR:" + e.getClass().getName();
        }
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = readLines(size);
        final Document doc = Jsoup.parse(unesc(lines.get(0).split("\t", -1)[1]));
        final int n = lines.size() - 1;
        final String[] qs = new String[n];
        for (int k = 0; k < n; k++) qs[k] = unesc(lines.get(k + 1).split("\t", -1)[1]);
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            final Elements all = doc.getAllElements();
            for (int k = 0; k < n; k++) {
                final StringBuilder sb = new StringBuilder();
                try {
                    final Evaluator ev = QueryParser.parse(qs[k]);
                    sb.append(ev.toString().replaceAll("@[0-9a-f]+", "@")).append('#');
                    for (int j = 0; j < all.size(); j++) if (ev.matches(doc, all.get(j))) sb.append(j).append(',');
                } catch (Selector.SelectorParseException e) {
                    sb.append("ERR:").append(e.getMessage());
                } catch (RuntimeException e) {
                    sb.append("ERR:").append(e.getClass().getName());
                }
                upd(md, sb.toString());
            }
            done(mode, n, 0, md, 0, 0);
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int k = 0; k < n; k++) {
                    try {
                        sink += QueryParser.parse(qs[k]).hashCode() & 1;
                    } catch (RuntimeException e) {
                        sink += 2;
                    }
                }
            }
            done(mode, n, repeat, null, (System.nanoTime() - t0) / 1e9, sink);
        }
    }
}
