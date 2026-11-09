package org.apache.commons.text.diff;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.List;

public class TCBench {
    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    static String render(EditScript<Character> script) {
        final StringBuilder sb = new StringBuilder();
        script.visit(new CommandVisitor<Character>() {
            public void visitInsertCommand(Character o) { sb.append('+').append(o); }
            public void visitKeepCommand(Character o) { sb.append('=').append(o); }
            public void visitDeleteCommand(Character o) { sb.append('-').append(o); }
        });
        return sb.append('|').append(script.getLCSLength()).append('|').append(script.getModifications()).toString();
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final String[] ls = new String[n], rs = new String[n];
        for (int k = 0; k < n; k++) {
            final String[] p = lines.get(k).split("\t", -1);
            ls[k] = p[0]; rs[k] = p[1];
        }
        final Method mth = StringsComparator.class.getDeclaredMethod("buildScript", int.class, int.class, int.class, int.class, EditScript.class);
        mth.setAccessible(true);
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                final StringsComparator c = new StringsComparator(ls[k], rs[k]);
                final EditScript<Character> sc = new EditScript<>();
                String r;
                try {
                    mth.invoke(c, 0, ls[k].length(), 0, rs[k].length(), sc);
                    r = render(sc);
                } catch (InvocationTargetException e) {
                    r = "!" + e.getCause().getClass().getName();
                }
                md.update((r + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            long ns = 0;
            for (int rep = 0; rep < repeat; rep++) {
                final StringsComparator[] cs = new StringsComparator[n];
                final EditScript<?>[] scs = new EditScript<?>[n];
                for (int k = 0; k < n; k++) { cs[k] = new StringsComparator(ls[k], rs[k]); scs[k] = new EditScript<Character>(); }
                final long t0 = System.nanoTime();
                for (int k = 0; k < n; k++) {
                    try {
                        mth.invoke(cs[k], 0, ls[k].length(), 0, rs[k].length(), scs[k]);
                    } catch (InvocationTargetException e) {
                        sink += 2;
                    }
                }
                ns += System.nanoTime() - t0;
                for (int k = 0; k < n; k++) sink += scs[k].getModifications();
            }
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + (ns / 1e9) + "}");
        }
    }
}
