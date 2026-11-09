package org.apache.commons.codec.language.bm;

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

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        final List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final PhoneticEngine[] engines = new PhoneticEngine[n];
        final String[] words = new String[n];
        final Languages.LanguageSet[] sets = new Languages.LanguageSet[n];
        for (int i = 0; i < n; i++) {
            final String[] f = lines.get(i).split(" ", 5);
            engines[i] = new PhoneticEngine(NameType.valueOf(f[0]), RuleType.valueOf(f[1]), Integer.parseInt(f[2]) == 1);
            words[i] = f[4];
            sets[i] = Integer.parseInt(f[3]) == 1 ? Languages.ANY_LANGUAGE : engines[i].getLang().guessLanguages(words[i]);
        }
        if (mode.equals("check")) {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int i = 0; i < n; i++) {
                String r;
                try {
                    r = engines[i].encode(words[i], sets[i]);
                } catch (Throwable t) {
                    r = "!" + t.getClass().getName();
                }
                md.update((r + "\n").getBytes(StandardCharsets.UTF_8));
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0;
            for (int i = 0; i < n; i++) {
                sink += engines[i].encode(words[i], sets[i]).length(); // warm-up (rule tables load lazily)
            }
            final long t0 = System.nanoTime();
            for (int rep = 0; rep < repeat; rep++) {
                for (int i = 0; i < n; i++) {
                    sink += engines[i].encode(words[i], sets[i]).length();
                }
            }
            final double el = (System.nanoTime() - t0) / 1e9;
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + el + "}");
        }
    }
}
