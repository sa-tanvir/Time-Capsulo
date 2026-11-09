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

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = readLines(size);
        final List<String> hays = new ArrayList<>();
        final List<int[]> gStart = new ArrayList<>(); // [firstQuery, endQuery)
        final List<Integer> delta = new ArrayList<>();
        final List<String> seq = new ArrayList<>();
        for (String line : lines) {
            final String[] p = line.split("\t", -1);
            if (p[0].equals("H")) {
                hays.add(unesc(p[1]));
                gStart.add(new int[]{seq.size(), seq.size()});
            } else {
                delta.add(Integer.parseInt(p[1]));
                seq.add(unesc(p[2]));
                gStart.get(gStart.size() - 1)[1] = seq.size();
            }
        }
        final int nq = seq.size();
        final int ng = hays.size();
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            final StringBuilder sb = new StringBuilder();
            for (int g = 0; g < ng; g++) {
                final CharacterReader r = new CharacterReader(hays.get(g));
                for (int q = gStart.get(g)[0]; q < gStart.get(g)[1]; q++) {
                    for (int j = 0; j < delta.get(q); j++) r.advance();
                    sb.append(r.nextIndexOf(seq.get(q))).append(',');
                }
                sb.append('\n');
            }
            upd(md, sb.toString());
            done(mode, nq, 0, md, 0, 0);
        } else {
            long sink = 0;
            long ns = 0;
            final CharacterReader[] rs = new CharacterReader[ng];
            for (int rep = 0; rep < repeat; rep++) {
                for (int g = 0; g < ng; g++) rs[g] = new CharacterReader(hays.get(g));
                final long t0 = System.nanoTime();
                for (int g = 0; g < ng; g++) {
                    final CharacterReader r = rs[g];
                    for (int q = gStart.get(g)[0]; q < gStart.get(g)[1]; q++) {
                        for (int j = delta.get(q); j > 0; j--) r.advance();
                        sink += r.nextIndexOf(seq.get(q));
                    }
                }
                ns += System.nanoTime() - t0;
            }
            done(mode, nq, repeat, null, ns / 1e9, sink);
        }
    }
}
