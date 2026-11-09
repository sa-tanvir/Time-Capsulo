package org.apache.commons.lang3.text;

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

    static int[] cfg, off, len; static String[] text;
    static StrSubstitutor[] subs;
    static java.lang.reflect.Method m;
    static StrBuilder[] bufs;
    static void prep() {
        bufs = new StrBuilder[text.length];
        for (int k = 0; k < bufs.length; k++) bufs[k] = new StrBuilder(text[k]);
    }

    static String doCall(int k) throws Throwable {
        final StrBuilder b = new StrBuilder(text[k]);
        final Object r = m.invoke(subs[cfg[k]], b, off[k], len[k], null);
        return "ret:" + r + " buf:" + b.toString();
    }

    static long fast(int k) throws Throwable {
        final Object r = m.invoke(subs[cfg[k]], bufs[k], off[k], len[k], null);
        return ((Integer) r).intValue();
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        text = new String[n]; cfg = new int[n]; off = new int[n]; len = new int[n];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k).split("\t", -1);
            cfg[k] = Integer.parseInt(p[0]);
            text[k] = rep(u(p[1]), Integer.parseInt(p[2]));
            off[k] = Integer.parseInt(p[3]);
            len[k] = text[k].length() - off[k] - Integer.parseInt(p[4]);
        }
        final Map<String, String> map = new HashMap<String, String>();
        map.put("animal", "quick brown fox"); map.put("target", "lazy dog"); map.put("a", "A"); map.put("b", "BB");
        map.put("name", "Bob"); map.put("greet", "Hello ${name}!"); map.put("n1", "${n2}"); map.put("n2", "<${n3}>");
        map.put("n3", "end"); map.put("empty", ""); map.put("num", "42"); map.put("key", "animal"); map.put("i", "2");
        map.put("item1", "first"); map.put("item2", "second"); map.put("item3", "third"); map.put("x1", "${a}${b}${a}");
        map.put("cyc1", "[${cyc2}]"); map.put("cyc2", "(${cyc1})"); map.put("self", "${self}");
        map.put("w1", "<<w2>>"); map.put("w2", "two"); map.put("dollar", "$${a}"); map.put("long", "0123456789abcdefghij");
        map.put("pre.fix", "dot"); map.put("sp ace", "spaced"); map.put("v0", "zero"); map.put("v1", "one");
        map.put("v2", "${v3}${v3}"); map.put("v3", "t"); map.put("v4", "%a%"); map.put("v5", "!<<a>>");
        subs = new StrSubstitutor[7];
        subs[0] = new StrSubstitutor(map);
        subs[1] = new StrSubstitutor(map, "<<", ">>", '!', "|");
        subs[2] = new StrSubstitutor(map); subs[2].setEnableSubstitutionInVariables(true);
        subs[3] = new StrSubstitutor(map); subs[3].setPreserveEscapes(true);
        subs[4] = new StrSubstitutor(map, "%", "%", '\\');
        subs[5] = new StrSubstitutor(map, "${", "}", '$', (String) null);
        subs[6] = new StrSubstitutor(map, "${", "}", '$', ":="); subs[6].setEnableSubstitutionInVariables(true); subs[6].setPreserveEscapes(true);
        m = StrSubstitutor.class.getDeclaredMethod("substitute", StrBuilder.class, int.class, int.class, List.class);
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
                prep();
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
