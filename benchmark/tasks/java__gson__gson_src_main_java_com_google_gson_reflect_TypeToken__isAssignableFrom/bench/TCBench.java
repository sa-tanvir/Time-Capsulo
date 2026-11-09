package com.google.gson.reflect;

import java.lang.reflect.Method;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.*;

public class TCBench {
    // ---- type hierarchy used by the workload ----
    interface I0<X> {}
    interface I1<X> extends I0<X> {}
    static class A<T> implements I1<T> {}
    static class B<U> extends A<List<U>> {}
    static class C extends B<String> {}
    static class E2<K, V> extends A<K> implements Comparable<V> { public int compareTo(V v) { return 0; } }
    interface J0<T> {}
    interface J1<T> extends J0<T> {}
    interface J2<T> extends J1<T> {}
    interface J3<T> extends J2<T> {}
    interface J4<T> extends J3<T> {}
    interface J5<T> extends J4<T> {}
    interface J6<T> extends J5<T> {}
    interface J7<T> extends J6<T> {}
    interface J8<T> extends J7<T> {}
    interface J9<T> extends J8<T> {}
    interface J10<T> extends J9<T> {}
    interface J11<T> extends J10<T> {}
    interface J12<T> extends J11<T> {}
    interface J13<T> extends J12<T> {}
    interface J14<T> extends J13<T> {}
    interface J15<T> extends J14<T> {}
    interface J16<T> extends J15<T> {}
    interface J17<T> extends J16<T> {}
    interface J18<T> extends J17<T> {}
    interface J19<T> extends J18<T> {}
    interface J20<T> extends J19<T> {}
    interface J21<T> extends J20<T> {}
    interface J22<T> extends J21<T> {}
    interface J23<T> extends J22<T> {}
    interface J24<T> extends J23<T> {}
    interface J25<T> extends J24<T> {}
    interface J26<T> extends J25<T> {}
    interface J27<T> extends J26<T> {}
    interface J28<T> extends J27<T> {}
    interface J29<T> extends J28<T> {}
    interface J30<T> extends J29<T> {}
    interface J31<T> extends J30<T> {}
    interface J32<T> extends J31<T> {}
    interface J33<T> extends J32<T> {}
    interface J34<T> extends J33<T> {}
    interface J35<T> extends J34<T> {}
    interface J36<T> extends J35<T> {}
    interface J37<T> extends J36<T> {}
    interface J38<T> extends J37<T> {}
    interface J39<T> extends J38<T> {}
    interface J40<T> extends J39<T> {}
    static class D40<T> implements J40<T> {}
    static class D39<T> extends D40<T> implements J39<T> {}
    static class D38<T> extends D39<T> implements J38<T> {}
    static class D37<T> extends D38<T> implements J37<T> {}
    static class D36<T> extends D37<T> implements J36<T> {}
    static class D35<T> extends D36<T> implements J35<T> {}
    static class D34<T> extends D35<T> implements J34<T> {}
    static class D33<T> extends D34<T> implements J33<T> {}
    static class D32<T> extends D33<T> implements J32<T> {}
    static class D31<T> extends D32<T> implements J31<T> {}
    static class D30<T> extends D31<T> implements J30<T> {}
    static class D29<T> extends D30<T> implements J29<T> {}
    static class D28<T> extends D29<T> implements J28<T> {}
    static class D27<T> extends D28<T> implements J27<T> {}
    static class D26<T> extends D27<T> implements J26<T> {}
    static class D25<T> extends D26<T> implements J25<T> {}
    static class D24<T> extends D25<T> implements J24<T> {}
    static class D23<T> extends D24<T> implements J23<T> {}
    static class D22<T> extends D23<T> implements J22<T> {}
    static class D21<T> extends D22<T> implements J21<T> {}
    static class D20<T> extends D21<T> implements J20<T> {}
    static class D19<T> extends D20<T> implements J19<T> {}
    static class D18<T> extends D19<T> implements J18<T> {}
    static class D17<T> extends D18<T> implements J17<T> {}
    static class D16<T> extends D17<T> implements J16<T> {}
    static class D15<T> extends D16<T> implements J15<T> {}
    static class D14<T> extends D15<T> implements J14<T> {}
    static class D13<T> extends D14<T> implements J13<T> {}
    static class D12<T> extends D13<T> implements J12<T> {}
    static class D11<T> extends D12<T> implements J11<T> {}
    static class D10<T> extends D11<T> implements J10<T> {}
    static class D9<T> extends D10<T> implements J9<T> {}
    static class D8<T> extends D9<T> implements J8<T> {}
    static class D7<T> extends D8<T> implements J7<T> {}
    static class D6<T> extends D7<T> implements J6<T> {}
    static class D5<T> extends D6<T> implements J5<T> {}
    static class D4<T> extends D5<T> implements J4<T> {}
    static class D3<T> extends D4<T> implements J3<T> {}
    static class D2<T> extends D3<T> implements J2<T> {}
    static class D1<T> extends D2<T> implements J1<T> {}
    static class D0<T> extends D1<T> implements J0<T> {}

    static List<String> listOfString; static List<Number> listOfNumber; static List<Integer> listOfInteger; static List<?> listOfUnknown;
    static List<? extends Number> listOfExtNumber; static Collection<String> collOfString; static Iterable<String> iterOfString;
    static Map<String, Integer> mapSI; static Map<String, String> mapSS; static Map<String, List<String>> mapSLS; static Set<String> setOfString;
    static Set<List<String>> setOfListOfString; static Comparable<String> cmpString; static ArrayList<String> alString; static ArrayList<Integer> alInteger;
    static HashMap<String, Integer> hmSI; static LinkedList<String> llString; static A<String> aString; static A<Integer> aInteger; static B<String> bString; static B<Integer> bInteger;
    static I0<String> i0String; static I1<String> i1String; static I1<Integer> i1Integer; static I0<List<String>> i0ListString; static List<String>[] arrListString;
    static E2<String, String> e2SS; static A<List<String>> aListString; static A<List<Integer>> aListInteger;

    static final Map<String, Type> CAT = new LinkedHashMap<String, Type>();
    static void f(String name, String field) throws Exception { CAT.put(name, TCBench.class.getDeclaredField(field).getGenericType()); }

    static void init() throws Exception {
        f("List<String>", "listOfString"); f("List<Number>", "listOfNumber"); f("List<Integer>", "listOfInteger"); f("List<?>", "listOfUnknown");
        f("List<? extends Number>", "listOfExtNumber"); f("Collection<String>", "collOfString"); f("Iterable<String>", "iterOfString");
        f("Map<String,Integer>", "mapSI"); f("Map<String,String>", "mapSS"); f("Map<String,List<String>>", "mapSLS"); f("Set<String>", "setOfString");
        f("Set<List<String>>", "setOfListOfString"); f("Comparable<String>", "cmpString"); f("ArrayList<String>", "alString"); f("ArrayList<Integer>", "alInteger");
        f("HashMap<String,Integer>", "hmSI"); f("LinkedList<String>", "llString"); f("A<String>", "aString"); f("A<Integer>", "aInteger"); f("B<String>", "bString");
        f("B<Integer>", "bInteger"); f("I0<String>", "i0String"); f("I1<String>", "i1String"); f("I1<Integer>", "i1Integer"); f("I0<List<String>>", "i0ListString");
        f("E2<String,String>", "e2SS"); f("A<List<String>>", "aListString"); f("A<List<Integer>>", "aListInteger");
        f("List<String>[]", "arrListString");
        CAT.put("C", C.class); CAT.put("ArrayList", ArrayList.class); CAT.put("String", String.class); CAT.put("Object", Object.class); CAT.put("Integer", Integer.class);
        CAT.put("A", A.class); CAT.put("B", B.class); CAT.put("List", List.class); CAT.put("int[]", int[].class);
        CAT.put("A<T>", TypeToken.getParameterized(A.class, A.class.getTypeParameters()[0]).getType());
        CAT.put("A<U>", TypeToken.getParameterized(A.class, B.class.getTypeParameters()[0]).getType());
        CAT.put("TV:T", A.class.getTypeParameters()[0]);
        CAT.put("WC:Number", ((ParameterizedType) CAT.get("List<? extends Number>")).getActualTypeArguments()[0]);
        CAT.put("null", null);
    }

    static Type resolve(String name) {
        if (name.length() > 2 && (name.charAt(0) == 'D' || name.charAt(0) == 'J') && Character.isDigit(name.charAt(1))) {
            int c = name.indexOf(':');
            Class<?> k = CHAIN_CLASSES.get(name.substring(0, c));
            String a = name.substring(c + 1);
            Type arg = a.equals("String") ? String.class : a.equals("Integer") ? Integer.class : Number.class;
            return TypeToken.getParameterized(k, arg).getType();
        }
        if (!CAT.containsKey(name)) throw new IllegalStateException("unknown type " + name);
        return CAT.get(name);
    }

    static final Map<String, Class<?>> CHAIN_CLASSES = new HashMap<String, Class<?>>();

    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    static void upd(MessageDigest md, String s) {
        md.update(s.getBytes(StandardCharsets.UTF_8));
        md.update((byte) 10);
    }

    static Map<String, Type> initMap(String spec) {
        Map<String, Type> m = new HashMap<String, Type>();
        if (!spec.isEmpty()) for (String kv : spec.split(",")) { String[] p = kv.split("="); m.put(p[0], resolve(p[1])); }
        return m;
    }

    public static void main(String[] args) throws Exception {
        final String size = args[0];
        final int repeat = Integer.parseInt(args[1]);
        final String mode = args[2];
        init();
        for (Class<?> k : TCBench.class.getDeclaredClasses()) {
            String n = k.getSimpleName();
            if (n.matches("[DJ]\\d+")) CHAIN_CLASSES.put(n, k);
        }
        final Method m = TypeToken.class.getDeclaredMethod("isAssignableFrom", Type.class, ParameterizedType.class, Map.class);
        m.setAccessible(true);
        List<String> lines = Files.readAllLines(Paths.get("/task/bench/workload_" + size + ".txt"), StandardCharsets.UTF_8);
        final int n = lines.size();
        final Type[] from = new Type[n]; final ParameterizedType[] to = new ParameterizedType[n]; final String[] init = new String[n];
        for (int k = 0; k < n; k++) {
            String[] p = lines.get(k).split("\t", -1);
            from[k] = resolve(p[0]);
            to[k] = (ParameterizedType) resolve(p[1]);
            init[k] = p.length > 2 ? p[2] : "";
        }
        if (mode.equals("check")) {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int k = 0; k < n; k++) {
                Map<String, Type> map = initMap(init[k]);
                String r;
                try {
                    r = String.valueOf(m.invoke(null, from[k], to[k], map));
                } catch (java.lang.reflect.InvocationTargetException e) {
                    r = "EX:" + e.getCause().getClass().getName() + ":" + e.getCause().getMessage();
                }
                TreeMap<String, String> sorted = new TreeMap<String, String>();
                for (Map.Entry<String, Type> e : map.entrySet()) sorted.put(e.getKey(), String.valueOf(e.getValue()));
                upd(md, r + "|" + sorted);
            }
            System.out.println("{\"cases\":" + n + ",\"output_digest\":\"" + hex(md.digest()) + "\"}");
        } else {
            long sink = 0, ns = 0;
            @SuppressWarnings("unchecked") Map<String, Type>[] maps = new Map[n];
            for (int rep = 0; rep < repeat; rep++) {
                for (int k = 0; k < n; k++) maps[k] = initMap(init[k]);
                long t0 = System.nanoTime();
                for (int k = 0; k < n; k++) {
                    try { sink += ((Boolean) m.invoke(null, from[k], to[k], maps[k])) ? 1 : 2; } catch (java.lang.reflect.InvocationTargetException e) { sink += 5; }
                }
                ns += System.nanoTime() - t0;
            }
            System.err.println("sink=" + sink);
            System.out.println("{\"cases\":" + n + ",\"repeat\":" + repeat + ",\"elapsed_s\":" + (ns / 1e9) + "}");
        }
    }
}
