package SistemadeCamaras;

import java.io.IOException;
import java.util.Random;

public class CamaraProcess {
    public static void main(String[] args) {
        int id = Integer.parseInt(args[0]);
        String zona = args[1];
        int duracion = 15;
        int frecuencia = 5;

        Random random = new Random();
        String[] eventos = {
            "Sin actividad",
            "Movimiento detectado",
            "Anomalía térmica",
            "Sombra extraña",
            "Ruido detectado"
        };

        int eventosParanormales = 0;
        int ciclos = duracion / frecuencia;

        for (int i = 0; i < ciclos; i++) {
            try {
                ProcessBuilder pb = new ProcessBuilder("sleep", "10");
                Process p = pb.start();
                p.waitFor();
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
            }

            // Evento aleatorio
            String evento = eventos[random.nextInt(eventos.length)];
            System.out.println("Cámara " + id + " | Zona: " + zona + " | Evento: " + evento);

            if (!evento.equals("Sin actividad")) {
                eventosParanormales++;
            }
        }

        System.out.println("Cámara " + id + " finalizó. Eventos paranormales detectados: " + eventosParanormales);
    }
}
