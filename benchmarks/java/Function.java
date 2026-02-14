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
}
