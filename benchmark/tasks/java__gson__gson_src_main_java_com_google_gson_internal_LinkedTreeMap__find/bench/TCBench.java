package com.google.gson.internal;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.*;

public class TCBench {
    static final boolean HASH = false;

    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    static void upd(MessageDigest md, String s) {
        md.update(s.getBytes(StandardCharsets.UTF_8));
        md.update((byte) 10);
    }

    static final class Key implements Comparable<Key> {
        final String name; final int hash;
        Key(String name, int hash) { this.name = name; this.hash = hash; }
        @Override public int compareTo(Key o) { return name.compareTo(o.name); }
        @Override public int hashCode() { return hash; }
        @Override public boolean equals(Object o) { return o instanceof Key && ((Key) o).name.equals(name); }
        @Override public String toString() { return name; }
    }

    static final class NC {
        @Override public int hashCode() { return 5; }
    }

    // operation codes
    static final int P = 0, R = 1, G = 2, F = 3, N = 4, C = 5, X = 6, Y = 7;

    static final class Case {
        boolean reverse;
        int[] type, idx;
        Key[] keys;
    }

    static String letters = "prgfncxy";

    static Case build(String[] p) {
        Case c = new Case();
        c.reverse = p[1].equals("R");
        int keyspace, hashmod;
        if (p[0].equals("E")) {
            // E <cmp> <hashmod> <keyspace> <ops...> : explicit ops, each token = letter + key index
            hashmod = Integer.parseInt(p[2]);
            keyspace = Integer.parseInt(p[3]);
            String[] toks = p[4].isEmpty() ? new String[0] : p[4].split(",");
            c.type = new int[toks.length]; c.idx = new int[toks.length];
            for (int i = 0; i < toks.length; i++) {
                c.type[i] = letters.indexOf(toks[i].charAt(0));
                c.idx[i] = Integer.parseInt(toks[i].substring(1));
            }
        } else {
            // G <cmp> <hashmod> <keyspace> <nops> <seed> <putPct> <remPct> <pattern>
            hashmod = Integer.parseInt(p[2]);
            keyspace = Integer.parseInt(p[3]);
            int nops = Integer.parseInt(p[4]);
            long seed = Long.parseLong(p[5]);
            int putPct = Integer.parseInt(p[6]), remPct = Integer.parseInt(p[7]);
            String pat = p[8];
            Random rnd = new Random(seed);
            c.type = new int[nops]; c.idx = new int[nops];
            int counter = 0;
            for (int i = 0; i < nops; i++) {
                int r = rnd.nextInt(100);
                int t;
                if (r < putPct) t = P;
                else if (r < putPct + remPct) t = R;
                else t = new int[]{G, F, N, C}[rnd.nextInt(4)];
                int k;
                if (t == P || t == N) {
                    switch (pat.charAt(0)) {
                        case 'A': k = counter++ % keyspace; break;
                        case 'D': k = keyspace - 1 - (counter++ % keyspace); break;
                        case 'Z': { int q = counter++; k = (q % 2 == 0) ? (q / 2) % keyspace : keyspace - 1 - (q / 2) % keyspace; break; }
                        default: k = rnd.nextInt(keyspace);
                    }
                } else {
                    k = rnd.nextInt(keyspace);
                }
                c.type[i] = t; c.idx[i] = k;
            }
        }
        c.keys = new Key[keyspace];
        for (int i = 0; i < keyspace; i++) c.keys[i] = new Key(String.format("k%07d", i), (i % hashmod) * 40503);
        return c;
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    static Object newMap(boolean reverse) {
        Comparator cmp = reverse ? Collections.reverseOrder() : null;
        if (HASH) return cmp == null ? new LinkedHashTreeMap<Key, Integer>() : new LinkedHashTreeMap<Key, Integer>(cmp);
        return cmp == null ? new LinkedTreeMap<Key, Integer>() : new LinkedTreeMap<Key, Integer>(cmp);
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    static long run(Object mo, Case c, StringBuilder sb) {
        long sink = 0;
        final int n = c.type.length;
        final int[] type = c.type, idx = c.idx;
        final Key[] keys = c.keys;
        LinkedTreeMap<Key, Integer> m = (LinkedTreeMap<Key, Integer>) mo;
        NC nc = new NC();
        for (int i = 0; i < n; i++) {
            Key k = keys[idx[i]];
            Object res = null;
            String ex = null;
            switch (type[i]) {
                case P: res = m.put(k, i); break;
                case R: res = m.remove(k); break;
                case G: res = m.get(k); break;
                case F: { LinkedTreeMap.Node<Key, Integer> nd = m.find(k, false); res = nd == null ? null : nd.key; break; }
                case N: { int before = m.size; LinkedTreeMap.Node<Key, Integer> nd = m.find(k, true); res = nd.key + ":" + (m.size - before) + ":" + nd.height; break; }
                case C: res = m.containsKey(k); break;
                case X: case Y:
                    try {
                        boolean create = type[i] == X;
                        boolean empty = m.size == 0;
                        Object o = ((LinkedTreeMap) (Object) m).find((Object) nc, create);
                        res = o == null ? null : "node";
                    } catch (RuntimeException e) {
                        ex = e.getClass().getName();
                        if (sb != null && type[i] == X && m.size == 0 && e instanceof ClassCastException) ex += ":" + e.getMessage();
                    }
                    break;
            }
            if (res instanceof Integer) sink += (Integer) res + 1;
            else if (res != null) sink += 3;
            if (ex != null) sink += 11;
            if (sb != null) { sb.append(type[i]).append('=').append(ex != null ? ex : String.valueOf(res)).append(';'); }
        }
        sink += m.size;
        return sink;
    }

    static void ser(StringBuilder sb, LinkedTreeMap.Node<Key, Integer> nd, LinkedTreeMap.Node<Key, Integer> parent) {
        sb.append('(').append(nd.key.name).append(':').append(nd.height);
        if (nd.parent != parent) sb.append('!');
        if (nd.left != null) { sb.append('L'); ser(sb, nd.left, nd); }
        if (nd.right != null) { sb.append('R'); ser(sb, nd.right, nd); }
        sb.append(')');
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    static void structure(Object mo, StringBuilder sb) {
        LinkedTreeMap<Key, Integer> m = (LinkedTreeMap<Key, Integer>) mo;
        sb.append("|size=").append(m.size()).append(",mod=").append(m.modCount);
        StringBuilder it = new StringBuilder("|iter=");
        for (Object eo : m.entrySet()) { Map.Entry e = (Map.Entry) eo; it.append(((Key) e.getKey()).name).append('=').append(e.getValue()).append(','); }
        sb.append(it);
        sb.append("|tree=");
        if (m.root != null) ser(sb, m.root, null);
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final Case[] cases = new Case[n];
        for (int k = 0; k < n; k++) cases[k] = build(lines.get(k).split("\t", -1));
        if (mode.equals("check")) {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                Object m = newMap(cases[k].reverse);
                StringBuilder sb = new StringBuilder();
                run(m, cases[k], sb);
                structure(m, sb);
                upd(md, sb.toString());
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0, ns = 0;
            Object[] maps = new Object[n];
            for (int rep = 0; rep < repeat; rep++) {
                for (int k = 0; k < n; k++) maps[k] = newMap(cases[k].reverse);
                long t0 = System.nanoTime();
                for (int k = 0; k < n; k++) sink += run(maps[k], cases[k], null);
                ns += System.nanoTime() - t0;
            }
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + (ns / 1e9) + "}");
        }
    }
}
