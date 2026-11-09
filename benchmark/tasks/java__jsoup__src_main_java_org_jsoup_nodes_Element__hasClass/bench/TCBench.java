package org.jsoup.nodes;

import org.jsoup.parser.Tag;

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
        final List<Element> els = new ArrayList<>();
        final List<List<String>> qs = new ArrayList<>();
        for (String line : lines) {
            final String[] p = line.split("\t", -1);
            if (p[0].equals("E")) {
                final Element e = new Element(Tag.valueOf("div"), "");
                if (!p[1].equals("none")) e.attr(p[1], unesc(p[2]));
                els.add(e);
                qs.add(new ArrayList<String>());
            } else {
                qs.get(qs.size() - 1).add(unesc(p[1]));
            }
        }
        int cases = 0;
        for (List<String> q : qs) cases += q.size();
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            final StringBuilder sb = new StringBuilder();
            for (int e = 0; e < els.size(); e++) {
                sb.setLength(0);
                for (String q : qs.get(e)) sb.append(els.get(e).hasClass(q) ? '1' : '0');
                upd(md, sb.toString());
            }
            done(mode, cases, 0, md, 0, 0);
        } else {
            long sink = 0;
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int e = 0; e < els.size(); e++) {
                    final Element el = els.get(e);
                    for (String q : qs.get(e)) if (el.hasClass(q)) sink++;
                }
            }
            done(mode, cases, repeat, null, (System.nanoTime() - t0) / 1e9, sink);
        }
    }
}
