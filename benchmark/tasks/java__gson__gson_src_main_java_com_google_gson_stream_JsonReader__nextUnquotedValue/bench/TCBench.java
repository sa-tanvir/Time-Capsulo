package com.google.gson.stream;

import java.io.IOException;
import java.io.Reader;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.*;

public class TCBench {
    static final String OP = "nextUnquotedValue";

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

    /** Reader that hands out at most `chunk` chars per read (0 = unlimited). */
    static final class Rd extends Reader {
        final String s; final int chunk; int pos;
        Rd(String s, int chunk) { this.s = s; this.chunk = chunk; }
        @Override public int read(char[] b, int off, int len) {
            if (pos >= s.length()) return -1;
            int n = Math.min(len, s.length() - pos);
            if (chunk > 0) n = Math.min(n, chunk);
            s.getChars(pos, pos + n, b, off);
            pos += n;
            return n;
        }
        @Override public void close() {}
    }

    static Field fld(String n) throws Exception { Field f = JsonReader.class.getDeclaredField(n); f.setAccessible(true); return f; }
    static Field fPos, fLimit, fLineNumber, fLineStart, fPeeked, fPeekedLong, fPeekedNumberLength;
    static Method mOp, mFill;

    static int abs(JsonReader r, Rd rd) throws Exception {
        return rd.pos - (fLimit.getInt(r) - fPos.getInt(r));
    }

    static final class Case {
        int chunk; boolean lenient; String text; int calls;
    }

    static JsonReader open(Case c, Rd[] rdOut) throws Exception {
        Rd rd = new Rd(c.text, c.chunk);
        JsonReader r = new JsonReader(rd);
        r.setLenient(c.lenient);
        mFill.invoke(r, 1);
        rdOut[0] = rd;
        return r;
    }

    static String locless(String m) {
        int i = m == null ? -1 : m.indexOf(" at line ");
        return i < 0 ? m : m.substring(0, i);
    }

    /** Runs the target on a primed reader; returns a sink value; appends observations to sb when non-null. */
    static long run(JsonReader r, Rd rd, Case c, StringBuilder sb) throws Exception {
        long sink = 0;
        String err = null;
        try {
            if (OP.equals("readEscapeCharacter")) {
                for (int k = 0; k < c.calls; k++) {
                    char ch = (Character) mOp.invoke(r);
                    sink += ch;
                    if (sb != null) sb.append((int) ch).append(',');
                }
            } else if (OP.equals("nextUnquotedValue")) {
                String s = (String) mOp.invoke(r);
                sink += s.length();
                if (sb != null) sb.append(s.length()).append(':').append(s);
            } else if (OP.equals("peekNumber")) {
                int ret = (Integer) mOp.invoke(r);
                sink += ret;
                if (sb != null) {
                    sb.append("ret=").append(ret).append(",peeked=").append(fPeeked.getInt(r));
                    if (ret == 15) sb.append(",long=").append(fPeekedLong.getLong(r));
                    if (ret == 16) sb.append(",len=").append(fPeekedNumberLength.getInt(r));
                }
            } else {
                mOp.invoke(r);
            }
        } catch (InvocationTargetException e) {
            Throwable t = e.getCause();
            sink += 7;
            if (sb != null) {
                String m = t.getMessage();
                if (!OP.equals("peekNumber") && !OP.equals("readEscapeCharacter")) m = locless(m);
                err = "EX:" + t.getClass().getName() + ":" + m;
            }
        }
        if (sb != null) {
            if (err != null) sb.append(err);
            sb.append("|abs=").append(abs(r, rd));
            if (OP.equals("readEscapeCharacter")) {
                sb.append("|ln=").append(fLineNumber.getInt(r))
                  .append("|ls=").append(rd.pos - fLimit.getInt(r) + fLineStart.getInt(r));
            }
        }
        return sink;
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        fPos = fld("pos"); fLimit = fld("limit"); fLineNumber = fld("lineNumber"); fLineStart = fld("lineStart");
        fPeeked = fld("peeked"); fPeekedLong = fld("peekedLong"); fPeekedNumberLength = fld("peekedNumberLength");
        mOp = JsonReader.class.getDeclaredMethod(OP); mOp.setAccessible(true);
        mFill = JsonReader.class.getDeclaredMethod("fillBuffer", int.class); mFill.setAccessible(true);

        List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final int[] chunk = new int[n]; final boolean[] len = new boolean[n]; final int[] calls = new int[n];
        final String[] pre = new String[n], unit = new String[n], suf = new String[n]; final int[] count = new int[n];
        for (int k = 0; k < n; k++) {
            String[] p = lines.get(k).split("\t", -1);
            chunk[k] = Integer.parseInt(p[0]);
            len[k] = p[1].equals("L");
            calls[k] = Integer.parseInt(p[2]);
            pre[k] = unesc(p[3]); unit[k] = unesc(p[4]); count[k] = Integer.parseInt(p[5]); suf[k] = unesc(p[6]);
        }
        final int B = 200;
        if (mode.equals("check")) {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                Case c = mk(chunk[k], len[k], calls[k], pre[k], unit[k], count[k], suf[k]);
                Rd[] rd = new Rd[1];
                JsonReader r = open(c, rd);
                StringBuilder sb = new StringBuilder();
                run(r, rd[0], c, sb);
                upd(md, sb.toString());
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0, ns = 0;
            Case[] cs = new Case[B]; JsonReader[] rs = new JsonReader[B]; Rd[] rds = new Rd[B];
            for (int rep = 0; rep < repeat; rep++) {
                for (int k0 = 0; k0 < n; k0 += B) {
                    int m = Math.min(B, n - k0);
                    Rd[] tmp = new Rd[1];
                    for (int j = 0; j < m; j++) {
                        int k = k0 + j;
                        cs[j] = mk(chunk[k], len[k], calls[k], pre[k], unit[k], count[k], suf[k]);
                        rs[j] = open(cs[j], tmp); rds[j] = tmp[0];
                    }
                    long t0 = System.nanoTime();
                    for (int j = 0; j < m; j++) sink += run(rs[j], rds[j], cs[j], null);
                    ns += System.nanoTime() - t0;
                }
            }
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + (ns / 1e9) + "}");
        }
    }

    static Case mk(int chunk, boolean lenient, int calls, String pre, String unit, int count, String suf) {
        StringBuilder sb = new StringBuilder(pre.length() + unit.length() * count + suf.length());
        sb.append(pre);
        for (int i = 0; i < count; i++) sb.append(unit);
        sb.append(suf);
        Case c = new Case();
        c.chunk = chunk; c.lenient = lenient; c.calls = calls; c.text = sb.toString();
        return c;
    }
}
