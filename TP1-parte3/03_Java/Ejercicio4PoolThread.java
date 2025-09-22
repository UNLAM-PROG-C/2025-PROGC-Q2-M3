import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ThreadPoolTest {
    public static void main(String[] args) {
        ExecutorService pool = Executors.newFixedThreadPool(10); // pool con 10 hilos

        long inicio = System.currentTimeMillis();

        for (int i = 1; i <= 1000; i++) {
            int tareaId = i;
            pool.submit(() -> {
                System.out.println("Tarea " + tareaId + " ejecutada por " +
                        Thread.currentThread().getName());
                try {
                    Thread.sleep(100); // simula trabajo de 100 ms
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            });
        }

        pool.shutdown();
        while (!pool.isTerminated()) {

        }

        long fin = System.currentTimeMillis();
        double tiempoSegundos = (fin - inicio) / 1000.0;
        System.out.println("Tiempo total: " + tiempoSegundos + " segundos");
    }
}

/*Conclusión

Teniendo en cuenta las tres ejecuciones realizadas en C#, Java y Python, podemos afirmar que el tiempo de procesamiento total es menor al ejecutar una tarea en un hilo individual (un hilo por tarea) en comparación con la ejecución mediante un thread pool. Sin embargo, esta afirmación resulta incompleta si no se consideran ciertos matices.

En primer lugar, utilizamos tareas principalmente I/O-bound. Si hubiéramos ejecutado tareas sin una gran proporción de operaciones de entrada/salida pero con alta carga de CPU, no existiría la ventaja de los tiempos de “espera” y del aprovechamiento de la concurrencia. En ese caso, los tiempos tenderían a igualarse y, probablemente, sería más conveniente utilizar un thread pool.

Otra desventaja de crear un hilo por tarea es el mayor consumo de memoria: cada hilo ocupa un espacio específico para su stack. En cambio, al usar un thread pool mantenemos una cantidad fija de hilos y, por lo tanto, un uso de memoria más controlado, reduciendo riesgos.

Además, observamos que, cuando la cantidad de tareas es menor, el tiempo de procesamiento tiende a igualarse. En este escenario, un thread pool también resulta más eficiente, ya que evita el costo de creación de hilos individuales para cada tarea.

En síntesis:

Para tareas I/O-bound largas o en gran volumen, crear un hilo por tarea puede mejorar significativamente los tiempos de procesamiento, aunque con un aumento considerable en el consumo de memoria.

Para tareas CPU-bound o muy cortas, el thread pool es claramente superior: limita la concurrencia a lo que la CPU puede aprovechar, reduce el overhead por creación de hilos y disminuye el uso de memoria.

Teniendo en cuenta estas premisas, la opción más recomendable en términos generales es utilizar un thread pool, ajustando la cantidad de hilos de acuerdo con la situación o el problema a resolver.
*/