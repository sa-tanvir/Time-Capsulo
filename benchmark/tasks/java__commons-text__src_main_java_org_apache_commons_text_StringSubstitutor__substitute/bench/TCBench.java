package org.apache.commons.text;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TCBench {
    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    static Map<String, String> vars() {
        final Map<String, String> m = new HashMap<>();
        final String[] base = { "alpha", "beta", "gamma", "delta", "eps", "zeta", "eta", "theta", "iota", "kappa" };
        for (int i = 0; i < 10; i++) m.put("v" + i, base[i]);
        for (int i = 10; i < 20; i++) m.put("v" + i, "[${v" + (i - 10) + "}/" + (i % 3 == 0 ? "$${v1}" : "${nokey:-q" + i + "}") + "]");
        m.put("v20", "");
        m.put("v21", "${v22}${v23}");
        m.put("v22", "<${v3}>");
        m.put("v23", "{${v2}}");
        m.put("v24", "$");
        m.put("v25", "${");
        m.put("v26", "${v27}!");
        m.put("v27", "mid ${v1} ${v28}");
        m.put("v28", "${v1}${v1}");
        m.put("v29", "end");
        m.put("n0", "1");
        m.put("n1", "2");
        m.put("n2", "11");
        m.put("cycA", "A${cycB}");
        m.put("cycB", "B${cycA}");
        return m;
    }

    static StringSubstitutor[] configs() {
        final StringSubstitutor c0 = new StringSubstitutor(vars());
        final StringSubstitutor c1 = new StringSubstitutor(vars());
        c1.setEnableSubstitutionInVariables(true);
        c1.setPreserveEscapes(true);
        final StringSubstitutor c2 = new StringSubstitutor(vars());
        c2.setDisableSubstitutionInValues(true);
        final StringSubstitutor c3 = new StringSubstitutor(vars());
        c3.setEnableUndefinedVariableException(true);
        c3.setEnableSubstitutionInVariables(true);
        return new StringSubstitutor[] { c0, c1, c2, c3 };
    }

    static String run(Method m, StringSubstitutor s, TextStringBuilder b, int off, int len) throws Exception {
        String r;
        try {
            r = "r" + m.invoke(s, b, off, len, null);
        } catch (InvocationTargetException e) {
            r = "!" + e.getCause().getClass().getName() + ":" + e.getCause().getMessage();
        }
        return r + "|" + b.toString();
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final String[] in = lines.toArray(new String[0]);
        final int n = in.length;
        final StringSubstitutor[] cfg = configs();
        final Method mth = StringSubstitutor.class.getDeclaredMethod("substitute", TextStringBuilder.class, int.class, int.class, List.class);
        mth.setAccessible(true);
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (final StringSubstitutor s : cfg) {
                for (int k = 0; k < n; k++) {
                    final int len = in[k].length();
                    final String r1 = run(mth, s, new TextStringBuilder(in[k]), 0, len);
                    final int off = Math.min(3, len), l2 = Math.max(0, len - off - Math.min(2, len - off));
                    final String r2 = run(mth, s, new TextStringBuilder(in[k]), off, l2);
                    md.update((r1 + "\n" + r2 + "\n").getBytes(StandardCharsets.UTF_8));
                }
            }
            System.out.println("{\"cases\":" + (2 * cfg.length * n) + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            long ns = 0;
            for (int rep = 0; rep < repeat; rep++) {
                final TextStringBuilder[][] bs = new TextStringBuilder[cfg.length][n];
                for (int c = 0; c < cfg.length; c++) for (int k = 0; k < n; k++) bs[c][k] = new TextStringBuilder(in[k]);
                final long t0 = System.nanoTime();
                for (int c = 0; c < cfg.length; c++) {
                    for (int k = 0; k < n; k++) {
                        try {
                            sink += (Integer) mth.invoke(cfg[c], bs[c][k], 0, bs[c][k].length(), null);
                        } catch (InvocationTargetException e) {
                            sink += 1;
                        }
                    }
                }
                ns += System.nanoTime() - t0;
                for (int c = 0; c < cfg.length; c++) for (int k = 0; k < n; k++) sink += bs[c][k].length();
            }
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + (cfg.length * n) + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + (ns / 1e9) + "}");
        }
    }
}
