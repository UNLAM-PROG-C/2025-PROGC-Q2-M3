import threading, time

def suma(numeros):
    total = 0
    for n in numeros:
        total += n
    return total

def worker_cpu(numeros):
    suma(numeros)

def medir_cpu_threads(N=10**7):
    lista = list(range(N))
    mitad = len(lista)//2

    t1 = threading.Thread(target=worker_cpu, args=(lista[:mitad],))
    t2 = threading.Thread(target=worker_cpu, args=(lista[mitad:],))

    inicio = time.time()
    t1.start(); t2.start()
    t1.join(); t2.join()
    return time.time() - inicio

print("Tiempo con 2 threads:", medir_cpu_threads())


'''
Ejercicio propuesto (GIL en Python): Escribe un programa que calcule la suma de una lista grande de números tanto con threads como con procesos, y mide el tiempo de ejecución de cada enfoque. Analiza los resultados: ¿cómo difieren los tiempos? Intenta luego reemplazar la tarea por una operación I/O-bound (por ejemplo, esperar una respuesta web en varios threads) y observa cómo en ese caso sí hay beneficio con threads. Discute por qué ocurre esta diferencia.
'''