import multiprocessing as mp, time

def tarea_io(t):
    time.sleep(t)

def medir_io_procesos():
    procesos = []
    inicio = time.time()
    for _ in range(5):
        p = mp.Process(target=tarea_io, args=(2,))
        procesos.append(p)
        p.start()
    for p in procesos:
        p.join()
    return time.time() - inicio

print("Tiempo I/O con procesos:", medir_io_procesos())


'''
Threads: Al usar threads para tareas I/O-bound, los tiempos se reducen considerablemente (aproximadamente el tiempo de la operación más larga, no la suma). Esto sucede porque durante las operaciones de espera (sleep, lectura de red, disco, etc.), el GIL se libera, permitiendo que otros hilos continúen ejecutándose mientras esperan.

Procesos: También funcionan en paralelo, pero tienen mayor overhead por crear procesos y copiar datos, por lo que en I/O-bound no siempre muestran ventaja sobre threads.

Conclusión I/O Bound: Para tareas I/O-bound en Python, threads sí proporcionan concurrencia real, a diferencia de las tareas CPU-bound, porque las operaciones de entrada/salida liberan el GIL y permiten que varios hilos progresen simultáneamente. Esto explica la diferencia en rendimiento respecto a las tareas CPU-bound.
'''