import java.io.*;
import java.util.*;
import java.util.concurrent.*;

public class CountCharacters {

    // Worker class implementing Runnable
    static class Worker implements Runnable {
        private List<String> lines;
        private int start, end;
        private long[] partialResults;
        private int index;

        public Worker(List<String> lines, int start, int end, long[] partialResults, int index) {
            this.lines = lines;
            this.start = start;
            this.end = end;
            this.partialResults = partialResults;
            this.index = index;
        }

        @Override
        public void run() {
            long count = 0;
            for (int i = start; i < end; i++) {
                // Quitar saltos de línea para que coincida con conteo esperado
                count += lines.get(i).replace("\r", "").replace("\n", "").length();
            }
            partialResults[index] = count;
        }
    }

    public static void main(String[] args) {

        String filePath = args[0];
        int nThreads = Integer.parseInt(args[1]);

        // Read file
        List<String> lines = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                lines.add(line);
            }
        } catch (IOException e) {
            System.out.println("Error: could not open the file.");
            return;
        }

        int totalLines = lines.size();
        if (nThreads > totalLines) {
            nThreads = totalLines; // no more threads than lines
        }

        long[] partialResults = new long[nThreads];
        Thread[] threads = new Thread[nThreads];

        long startTime = System.nanoTime();

        // Divide work among threads
        int block = totalLines / nThreads;
        int remainder = totalLines % nThreads;

        int startLine = 0;
        for (int i = 0; i < nThreads; i++) {
            int endLine = startLine + block + (i < remainder ? 1 : 0);
            threads[i] = new Thread(new Worker(lines, startLine, endLine, partialResults, i));
            threads[i].start();
            startLine = endLine;
        }

        // Wait for all threads
        for (int i = 0; i < nThreads; i++) {
            try {
                threads[i].join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        // Sum results
        long totalResult = 0;
        for (long pr : partialResults) {
            totalResult += pr;
        }

        // Fin de medición de tiempo y cálculo en milisegundos
        long endTime = System.nanoTime();
        double durationSeconds = (endTime - startTime) / 1e9;          // duración total en segundos
        double totalMilliseconds = durationSeconds * 1000;             // convertir a ms

        double averageOneLineMs = totalMilliseconds / totalLines;           // promedio por línea
        double averageHalfLinesMs = totalMilliseconds / (totalLines / 2.0); // promedio por L/2 líneas

        // Imprimir resultados
        System.out.println("Total Result (number of characters): " + totalResult);
        System.out.println("Total processing time: " + totalMilliseconds + " ms");
        System.out.println("Average time per line: " + averageOneLineMs + " ms");
        System.out.println("Average time per L/2 lines: " + averageHalfLinesMs + " ms");

        }
}