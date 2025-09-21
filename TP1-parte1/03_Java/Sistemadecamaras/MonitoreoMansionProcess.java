package SistemadeCamaras;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class MonitoreoMansionProcess {
    public static void main(String[] args) {
        int duracion = 20;
        int frecuencia = 5;

        String[] zonas = {"Sótano", "Ático", "Cocina", "Dormitorio", "Jardín", "Mausoleo"};
        List<Process> procesos = new ArrayList<>();

        for (int i = 0; i < zonas.length; i++) {
            List<String> command = new ArrayList<>();

            command.add("java");
            command.add("-cp");
            command.add(".");
            command.add("SistemadeCamaras.CamaraProcess");
            command.add(String.valueOf(i + 1));
            command.add(zonas[i]);

            ProcessBuilder pb = new ProcessBuilder(command);
            pb.inheritIO();
            try {
                Process p = pb.start();
                procesos.add(p);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        // Esperar a que todas las cámaras terminen
        for (Process p : procesos) {
            try {
                p.waitFor();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        System.out.println("Monitoreo finalizado. Todas las cámaras completaron su tarea.");
    }
}
