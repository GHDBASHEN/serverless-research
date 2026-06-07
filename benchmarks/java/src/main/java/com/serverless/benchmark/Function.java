package com.serverless.benchmark;

import java.util.Map;
import java.util.HashMap;
import java.util.Random;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.nio.file.Files;
import java.nio.file.Path;

public class Function {
    
    private static boolean isCold = true;

    // Inner class for Request/Response to keep it simple without heavy dependencies if possible
    public static class Request {
        public String workload;
        public int size;

        public String getWorkload() { return workload; }
        public void setWorkload(String workload) { this.workload = workload; }
        public int getSize() { return size; }
        public void setSize(int size) { this.size = size; }
    }

    public static class Response {
        public double duration_ms;
        public double memory_mb;
        public boolean cold_start;
        
        public Response(double duration_ms, double memory_mb, boolean cold_start) {
            this.duration_ms = duration_ms;
            this.memory_mb = memory_mb;
            this.cold_start = cold_start;
        }
    }

    public Response handleRequest(Request request) {
        long startTime = System.nanoTime();
        
        String workload = request.workload != null ? request.workload : "float_ops";
        int size = request.size > 0 ? request.size : 1000;
        
        if (workload.equals("fibonacci")) {
            fib(size);
        } else if (workload.equals("matrix_mult")) {
            matrixMult(size);
        } else if (workload.equals("prime_sieve")) {
            primeSieve(size);
        } else if (workload.equals("file_io")) {
            fileIo(size);
        } else if (workload.equals("float_ops")) {
            floatOps(size);
        } else if (workload.equals("cpu_math_1")) {
            cpu_math_1(size);
        } else if (workload.equals("cpu_math_2")) {
            cpu_math_2(size);
        } else if (workload.equals("cpu_math_3")) {
            cpu_math_3(size);
        } else if (workload.equals("cpu_math_4")) {
            cpu_math_4(size);
        } else if (workload.equals("cpu_math_5")) {
            cpu_math_5(size);
        } else if (workload.equals("mem_alloc_1")) {
            mem_alloc_1(size);
        } else if (workload.equals("mem_alloc_2")) {
            mem_alloc_2(size);
        } else if (workload.equals("mem_alloc_3")) {
            mem_alloc_3(size);
        } else if (workload.equals("mem_string_4")) {
            mem_string_4(size);
        } else if (workload.equals("mem_dict_5")) {
            mem_dict_5(size);
        } else if (workload.equals("disk_io_1")) {
            disk_io_1(size);
        } else if (workload.equals("disk_io_2")) {
            disk_io_2(size);
        } else if (workload.equals("disk_io_3")) {
            disk_io_3(size);
        } else if (workload.equals("disk_io_4")) {
            disk_io_4(size);
        } else if (workload.equals("disk_io_5")) {
            disk_io_5(size);
        } else if (workload.equals("net_sim_1")) {
            net_sim_1(size);
        } else if (workload.equals("net_sim_2")) {
            net_sim_2(size);
        } else if (workload.equals("net_sim_3")) {
            net_sim_3(size);
        } else if (workload.equals("net_sim_4")) {
            net_sim_4(size);
        } else if (workload.equals("net_sim_5")) {
            net_sim_5(size);
        } else if (workload.equals("data_proc_1")) {
            data_proc_1(size);
        } else if (workload.equals("data_proc_2")) {
            data_proc_2(size);
        } else if (workload.equals("data_proc_3")) {
            data_proc_3(size);
        } else if (workload.equals("data_proc_4")) {
            data_proc_4(size);
        } else if (workload.equals("data_proc_5")) {
            data_proc_5(size);
        } else if (workload.equals("crypto_1")) {
            crypto_1(size);
        } else if (workload.equals("crypto_2")) {
            crypto_2(size);
        } else if (workload.equals("crypto_3")) {
            crypto_3(size);
        } else if (workload.equals("crypto_4")) {
            crypto_4(size);
        } else if (workload.equals("crypto_5")) {
            crypto_5(size);
        } else if (workload.equals("web_biz_1")) {
            web_biz_1(size);
        } else if (workload.equals("web_biz_2")) {
            web_biz_2(size);
        } else if (workload.equals("web_biz_3")) {
            web_biz_3(size);
        } else if (workload.equals("web_biz_4")) {
            web_biz_4(size);
        } else if (workload.equals("web_biz_5")) {
            web_biz_5(size);
        } else if (workload.equals("sci_1")) {
            sci_1(size);
        } else if (workload.equals("sci_2")) {
            sci_2(size);
        } else if (workload.equals("sci_3")) {
            sci_3(size);
        } else if (workload.equals("sci_4")) {
            sci_4(size);
        } else if (workload.equals("sci_5")) {
            sci_5(size);
        }

        long endTime = System.nanoTime();
        double durationMs = (endTime - startTime) / 1_000_000.0;
        
        // Memory usage
        Runtime runtime = Runtime.getRuntime();
        double memoryMb = (runtime.totalMemory() - runtime.freeMemory()) / (1024.0 * 1024.0);
        
        boolean coldStartStatus = isCold;
        isCold = false;
        
        return new Response(durationMs, memoryMb, coldStartStatus);
    }
    
    // Algorithms
    
    private long fib(int n) {
        if (n <= 1) return n;
        return fib(n-1) + fib(n-2);
    }
    
    private void matrixMult(int n) {
        double[][] A = new double[n][n];
        double[][] B = new double[n][n];
        double[][] C = new double[n][n];
        Random rand = new Random();
        
        for(int i=0; i<n; i++) {
            for(int j=0; j<n; j++) {
                A[i][j] = rand.nextDouble();
                B[i][j] = rand.nextDouble();
            }
        }
        
        for(int i=0; i<n; i++) {
            for(int j=0; j<n; j++) {
                for(int k=0; k<n; k++) {
                    C[i][j] += A[i][k] * B[k][j];
                }
            }
        }
    }
    
    private void primeSieve(int n) {
        if (n < 2) return;
        boolean[] primes = new boolean[n+1];
        for(int i=0; i<=n; i++) primes[i] = true;
        
        for(int p = 2; p*p <= n; p++) {
            if(primes[p]) {
                for(int i = p*p; i <= n; i += p)
                    primes[i] = false;
            }
        }
    }
    
    private void fileIo(int size) {
        File file = new File("/tmp/test_" + System.nanoTime() + ".txt");
        try {
            byte[] data = new byte[size];
            // Write
            FileOutputStream fos = new FileOutputStream(file);
            fos.write(data);
            fos.close();
            
            // Read
            FileInputStream fis = new FileInputStream(file);
            byte[] readData = new byte[size];
            fis.read(readData);
            fis.close();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            file.delete();
        }
    }
    
    private void floatOps(int n) {
        double val = 1.0;
        for(int i=0; i<n; i++) {
            val = Math.sin(val) * Math.cos(val) + Math.tan(val);
        }
    }
    private void cpu_math_1(int size) {
        double val = 0; for(int i=0; i<size*1000; i++) val += Math.sin(i);
    }
    private void cpu_math_2(int size) {
        double val = 1; for(int i=0; i<size*100; i++) val = Math.pow(val * 1.0001, 1.01);
    }
    private void cpu_math_3(int size) {
        double val = 0; for(int i=0; i<size*500; i++) { double f=1; for(int j=1; j<=(i%50); j++) f*=j; val+=f; }
    }
    private void cpu_math_4(int size) {
        double val = 0; for(int i=0; i<size*1000; i++) val += Math.sqrt(i);
    }
    private void cpu_math_5(int size) {
        double val = 0; Random r = new Random(); double[] v1 = new double[size*100]; double[] v2 = new double[size*100]; for(int i=0; i<size*100; i++) { v1[i]=r.nextDouble(); v2[i]=r.nextDouble(); val+=v1[i]*v2[i]; }
    }
    private void mem_alloc_1(int size) {
        int[] arr = new int[size*10000]; for(int i=0; i<arr.length; i++) arr[i]=i;
    }
    private void mem_alloc_2(int size) {
        java.util.Map<String,Integer> map = new java.util.HashMap<>(); for(int i=0; i<size*5000; i++) map.put(String.valueOf(i), i);
    }
    private void mem_alloc_3(int size) {
        int[][] arr = new int[size*2000][10]; for(int i=0; i<size*2000; i++) for(int j=0; j<10; j++) arr[i][j]=i;
    }
    private void mem_string_4(int size) {
        StringBuilder sb = new StringBuilder(); for(int i=0; i<size*10000; i++) sb.append('x'); sb.toString();
    }
    private void mem_dict_5(int size) {
        java.util.Map<String, java.util.Map<String, Integer>> d = new java.util.HashMap<>(); for(int i=0; i<size*1000; i++) { java.util.Map<String,Integer> in = new java.util.HashMap<>(); in.put("nested", i); d.put("key_"+i, in); }
    }
    private void disk_io_1(int size) {
        try { File f = File.createTempFile("d1",".txt"); java.io.FileWriter fw = new java.io.FileWriter(f); for(int i=0; i<size*1000; i++) fw.write("A"); fw.close(); f.delete(); } catch(Exception e){}
    }
    private void disk_io_2(int size) {
        try { File f = File.createTempFile("d2",".txt"); java.io.FileWriter fw = new java.io.FileWriter(f); for(int i=0; i<size*2000; i++) fw.write("B"); fw.close(); f.delete(); } catch(Exception e){}
    }
    private void disk_io_3(int size) {
        try { File f = File.createTempFile("d3",".txt"); java.io.FileOutputStream fos = new java.io.FileOutputStream(f); byte[] b = new byte[size*500]; new Random().nextBytes(b); fos.write(b); fos.close(); f.delete(); } catch(Exception e){}
    }
    private void disk_io_4(int size) {
        try { File f = File.createTempFile("d4",".txt"); java.io.FileWriter fw = new java.io.FileWriter(f); for(int i=0; i<size*100; i++) fw.write(String.valueOf(i)); fw.close(); f.delete(); } catch(Exception e){}
    }
    private void disk_io_5(int size) {
        try { File f = File.createTempFile("d5",".txt"); java.io.FileWriter fw = new java.io.FileWriter(f); for(int i=0; i<size*100; i++) fw.write("X"); fw.close(); java.nio.file.Files.readAllBytes(f.toPath()); f.delete(); } catch(Exception e){}
    }
    private void net_sim_1(int size) {
        try { Thread.sleep(Math.min((long)(size * 1), 2000)); } catch(Exception e){}
    }
    private void net_sim_2(int size) {
        try { Thread.sleep(Math.min((long)(size * 2), 2000)); } catch(Exception e){}
    }
    private void net_sim_3(int size) {
        try { Thread.sleep(Math.min((long)(size * 3), 2000)); } catch(Exception e){}
    }
    private void net_sim_4(int size) {
        try { Thread.sleep(Math.min((long)(size * 4), 2000)); } catch(Exception e){}
    }
    private void net_sim_5(int size) {
        try { Thread.sleep(Math.min((long)(size * 5), 2000)); } catch(Exception e){}
    }
    private void data_proc_1(int size) {
        StringBuilder sb = new StringBuilder(); for(int i=0; i<size*100; i++) { sb.append(i); if(i<size*100-1) sb.append(","); } int val = sb.toString().split(",").length;
    }
    private void data_proc_2(int size) {
        StringBuilder sb = new StringBuilder(); sb.append("["); for(int i=0; i<size*100; i++) { sb.append("{\"id\":").append(i).append("}"); if(i<size*100-1) sb.append(","); } sb.append("]"); String j = sb.toString();
    }
    private void data_proc_3(int size) {
        byte[] b = new byte[size*100]; new Random().nextBytes(b); String enc = java.util.Base64.getEncoder().encodeToString(b); java.util.Base64.getDecoder().decode(enc);
    }
    private void data_proc_4(int size) {
        int val = 0; for(int i=0; i<size*1000; i++) { if(i%2==0 && i%3==0) val++; }
    }
    private void data_proc_5(int size) {
        StringBuilder sb = new StringBuilder(); for(int i=0; i<size*100; i++) sb.append("abc 123 "); java.util.regex.Matcher m = java.util.regex.Pattern.compile("\\d+").matcher(sb.toString()); int val=0; while(m.find()) val++;
    }
    private void crypto_1(int size) {
        try { java.security.MessageDigest md = java.security.MessageDigest.getInstance("MD5"); for(int i=0; i<size*100; i++) md.digest(String.valueOf(i).getBytes()); } catch(Exception e){}
    }
    private void crypto_2(int size) {
        try { java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-1"); for(int i=0; i<size*100; i++) md.digest(String.valueOf(i).getBytes()); } catch(Exception e){}
    }
    private void crypto_3(int size) {
        try { java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-256"); for(int i=0; i<size*100; i++) md.digest(String.valueOf(i).getBytes()); } catch(Exception e){}
    }
    private void crypto_4(int size) {
        try { java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-512"); for(int i=0; i<size*100; i++) md.digest(String.valueOf(i).getBytes()); } catch(Exception e){}
    }
    private void crypto_5(int size) {
        try { javax.crypto.spec.PBEKeySpec spec = new javax.crypto.spec.PBEKeySpec("pass".toCharArray(), "salt".getBytes(), size*100, 256); javax.crypto.SecretKeyFactory skf = javax.crypto.SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256"); skf.generateSecret(spec).getEncoded(); } catch(Exception e){}
    }
    private void web_biz_1(int size) {
        double val=0; Random r = new Random(); for(int i=0; i<size*10; i++) val += (r.nextDouble()*100) * (r.nextInt(5)+1);
    }
    private void web_biz_2(int size) {
        int val=0; Random r = new Random(); for(int i=0; i<size*100; i++) { if(r.nextBoolean()) val++; }
    }
    private void web_biz_3(int size) {
        StringBuilder sb = new StringBuilder(); for(int i=0; i<size*10; i++) sb.append("<h1>Header</h1>"); sb.toString().replace("h1>", "h2>");
    }
    private void web_biz_4(int size) {
        StringBuilder sb = new StringBuilder(); Random r = new Random(); String chars = "abcdef"; for(int i=0; i<size*100; i++) sb.append(chars.charAt(r.nextInt(chars.length())));
    }
    private void web_biz_5(int size) {
        java.util.List<Integer> list = new java.util.ArrayList<>(); Random r = new Random(); for(int i=0; i<size*100; i++) list.add(r.nextInt(100)); java.util.Collections.sort(list);
    }
    private void sci_1(int size) {
        double[] d = new double[size*100]; Random r = new Random(); double sum=0; for(int i=0; i<d.length; i++) { d[i]=r.nextDouble(); sum+=d[i]; } double mean=sum/d.length; double val=0; for(double x : d) val += Math.pow(x-mean, 2);
    }
    private void sci_2(int size) {
        double sum=0; Random r = new Random(); for(int i=0; i<size*100; i++) { sum+=i; sum+=(i*2+r.nextDouble()); }
    }
    private void sci_3(int size) {
        double[] d = new double[size*100]; Random r = new Random(); double max=0; for(int i=0; i<d.length; i++) { d[i]=r.nextDouble(); if(d[i]>max) max=d[i]; } for(int i=0; i<d.length; i++) d[i]/=max;
    }
    private void sci_4(int size) {
        int in=0; Random r = new Random(); int total = size*100; for(int i=0; i<total; i++) { if(Math.pow(r.nextDouble(),2)+Math.pow(r.nextDouble(),2) <= 1) in++; } double val = in * 4.0 / total;
    }
    private void sci_5(int size) {
        double val=0; for(int i=1; i<size*100; i++) val+=Math.log(i);
    }

}
