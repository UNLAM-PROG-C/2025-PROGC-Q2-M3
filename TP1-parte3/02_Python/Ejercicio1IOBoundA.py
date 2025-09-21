import threading, time

def tarea_io(t):
    time.sleep(t)

def medir_io_threads():
    hilos = []
    inicio = time.time()
    for _ in range(5):
        t = threading.Thread(target=tarea_io, args=(2,))
        hilos.append(t)
        t.start()
    for t in hilos:
        t.join()
    return time.time() - inicio

print("Tiempo I/O con threads:", medir_io_threads())

