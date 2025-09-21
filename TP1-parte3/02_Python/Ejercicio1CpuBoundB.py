import multiprocessing as mp, time

def suma(numeros):
    total = 0
    for n in numeros:
        total += n
    return total

def worker_cpu(numeros):
    suma(numeros)

def medir_cpu_procesos(N=10**7):
    lista = list(range(N))
    mitad = len(lista)//2

    p1 = mp.Process(target=worker_cpu, args=(lista[:mitad],))
    p2 = mp.Process(target=worker_cpu, args=(lista[mitad:],))

    inicio = time.time()
    p1.start(); p2.start()
    p1.join(); p2.join()
    return time.time() - inicio

print("Tiempo con 2 procesos:", medir_cpu_procesos())


'''
Conclusion CPU Bound:

En este ejercicio comparamos la suma de una lista grande de números usando threads y procesos en Python, observando el efecto del GIL.

Con threads, el tiempo de ejecución es casi igual al de un solo hilo, porque el GIL impide que más de un hilo ejecute código Python simultáneamente. Por eso, no se logra paralelismo real en tareas CPU-bound.

Con procesos, cada uno tiene su propio intérprete y GIL, lo que permite ejecutar cálculos en paralelo. Al dividir la carga entre dos procesos, el tiempo de ejecución se reduce aproximadamente a la mitad, mostrando el beneficio del paralelismo en CPU-bound.
'''