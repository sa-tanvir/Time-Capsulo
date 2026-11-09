package com.google.gson.internal.bind;

import com.google.gson.*;
import com.google.gson.stream.JsonToken;
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

    static void upd(MessageDigest md, String s) {
        md.update(s.getBytes(StandardCharsets.UTF_8));
        md.update((byte) 10);
    }

    static final class Gen {
        final Random rnd; final int target, maxDepth, fan; int count;
        Gen(long seed, int target, int maxDepth, int fan) { rnd = new Random(seed); this.target = target; this.maxDepth = maxDepth; this.fan = fan; }
        JsonElement elem(int depth) {
            count++;
            int r = rnd.nextInt(100);
            if (depth < maxDepth && count < target && r < 38) {
                int n = rnd.nextInt(fan + 1);
                if (r < 19) {
                    JsonArray a = new JsonArray();
                    for (int i = 0; i < n && count < target; i++) a.add(elem(depth + 1));
                    return a;
                } else {
                    JsonObject o = new JsonObject();
                    for (int i = 0; i < n && count < target; i++) o.add("k" + rnd.nextInt(1000) + "_" + i, elem(depth + 1));
                    return o;
                }
            }
            switch (rnd.nextInt(7)) {
                case 0: return new JsonPrimitive("s" + rnd.nextInt(100000));
                case 1: return new JsonPrimitive(rnd.nextInt());
                case 2: return new JsonPrimitive(rnd.nextDouble());
                case 3: return new JsonPrimitive(rnd.nextBoolean());
                case 4: return JsonNull.INSTANCE;
                case 5: return new JsonPrimitive(rnd.nextLong());
                default: return new JsonObject();
            }
        }
        JsonElement top() {
            JsonArray a = new JsonArray();
            while (count < target) a.add(elem(1));
            return a;
        }
    }

    static final class Case { char variant; JsonElement tree; }

    /** Walks the whole document; returns a sink value, records tokens when sb != null. */
    static long walk(Case cs, StringBuilder sb) throws Exception {
        long sink = 0;
        char v = cs.variant;
        JsonTreeReader r = new JsonTreeReader(cs.tree);
        if (v == 'C') {
            r.close();
            try { r.peek(); sink += 1; } catch (IllegalStateException e) { sink += 2; if (sb != null) sb.append("ISE:").append(e.getMessage()); }
            return sink;
        }
        int c = 0;
        while (true) {
            JsonToken t = r.peek();
            if (v == 'P' && c % 4 == 0) {
                JsonToken t2 = r.peek();
                boolean h = r.hasNext();
                sink += t2.ordinal() + (h ? 1 : 0);
                if (sb != null) sb.append(t2.ordinal()).append(h ? 'h' : 'n').append(';');
            }
            sink += t.ordinal();
            if (sb != null) {
                sb.append(t.ordinal());
                if (c % 8 == 0) sb.append('@').append(r.getPath());
                sb.append(',');
            }
            if (t == JsonToken.END_DOCUMENT) {
                if (v == 'D') { sink += r.peek().ordinal(); sink += r.peek().ordinal(); }
                break;
            }
            c++;
            switch (t) {
                case BEGIN_ARRAY:
                    if (v == 'S' && c % 3 == 0) r.skipValue();
                    else { if (v == 'M' && c % 5 == 0) mis(r, sb, 0); r.beginArray(); }
                    break;
                case BEGIN_OBJECT:
                    if (v == 'S' && c % 3 == 0) r.skipValue();
                    else { if (v == 'M' && c % 5 == 0) mis(r, sb, 1); r.beginObject(); }
                    break;
                case END_ARRAY: r.endArray(); break;
                case END_OBJECT: r.endObject(); break;
                case NAME:
                    if (v == 'S' && c % 7 == 0) r.skipValue();
                    else { if (v == 'M' && c % 5 == 0) mis(r, sb, 2); sink += r.nextName().length(); }
                    break;
                case STRING:
                    if (v == 'S' && c % 4 == 0) r.skipValue(); else sink += r.nextString().length();
                    break;
                case NUMBER:
                    if (c % 2 == 0) sink += (long) r.nextDouble(); else sink += r.nextString().length();
                    break;
                case BOOLEAN: if (r.nextBoolean()) sink++; break;
                case NULL: r.nextNull(); break;
                default: throw new IllegalStateException();
            }
        }
        return sink;
    }

    static void mis(JsonTreeReader r, StringBuilder sb, int kind) throws Exception {
        try {
            if (kind == 0) r.nextBoolean(); else if (kind == 1) r.nextString(); else r.endObject();
        } catch (IllegalStateException e) {
            if (sb != null) sb.append("ISE:").append(e.getMessage()).append(';');
        }
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final Case[] cases = new Case[n];
        for (int k = 0; k < n; k++) {
            String[] p = lines.get(k).split("\t", -1);
            Case c = new Case();
            c.variant = p[1].charAt(0);
            if (p[0].equals("X")) c.tree = new JsonParser().parse(unesc(p[2]));
            else c.tree = new Gen(Long.parseLong(p[2]), Integer.parseInt(p[3]), Integer.parseInt(p[4]), Integer.parseInt(p[5])).top();
            cases[k] = c;
        }
        if (mode.equals("check")) {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                StringBuilder sb = new StringBuilder();
                walk(cases[k], sb);
                upd(md, sb.toString());
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++)
                for (int k = 0; k < n; k++) sink += walk(cases[k], null);
            double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
