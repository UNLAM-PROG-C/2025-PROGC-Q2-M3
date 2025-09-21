import time
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# --- chequeo si es primo
def es_primo(num):
    if num < 2:
        return False
    if num % 2 == 0 and num > 2:
        return False
    for i in range(3, int(num**0.5) + 1, 2):
        if num % i == 0:
            return False
    return True

def n_esimo_primo(n):
    contador = 0
    numero = 1
    while contador < n:
        numero += 1
        if es_primo(numero):
            contador += 1
    return numero


valores = [100000, 200000, 300000, 400000]  # dejamos valores grandes para acentuar la diferencia

# --- Ejecución secuencial
def secuencial():
    inicio = time.time()
    resultados = [n_esimo_primo(n) for n in valores]
    fin = time.time()
    print("Secuencial:", resultados, f"Tiempo: {fin - inicio:.2f} s")

# --- Ejecución "concurrente" con ThreadPoolExecutor
def concurrente_threads():
    inicio = time.time()
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futuros = [executor.submit(n_esimo_primo, n) for n in valores]
        resultados = [f.result() for f in as_completed(futuros)]
    fin = time.time()
    print("Concurrente (ThreadPool):", resultados, f"Tiempo: {fin - inicio:.2f} s")

# --- Ejecución concurrente con ProcessPoolExecutor
def concurrente_procesos():
    inicio = time.time()
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futuros = [executor.submit(n_esimo_primo, n) for n in valores]
        resultados = [f.result() for f in as_completed(futuros)]
    fin = time.time()
    print("Concurrente (ProcessPool):", resultados, f"Tiempo: {fin - inicio:.2f} s")

# --- Main
if __name__ == "__main__":
    secuencial()
    concurrente_threads()
    concurrente_procesos()


'''
Ejercicio propuesto (Futures): Implementa un programa que lance varias tareas concurrentes que calculen, por ejemplo, el número primo 
n-ésimo para diferentes n grandes, usando Futures. Hazlo en tu lenguaje preferido (p. ej., Python con ThreadPoolExecutor, Java con 
CompletableFuture, o C# con Task). Usa la función de coordinación disponible (como Task.WhenAll o similar) para esperar todos los resultados 
y mostrarlos. Mide el tiempo total comparado con ejecutar las mismas cálculos en secuencia en un solo thread. Opcional: experimenta con 
cancelar una de las tareas a mitad de camino si tu entorno lo permite, para ver cómo se maneja la cancelación de futures.
'''

'''
Conclusion: al realizar la ejecucion con numeros muy grandes intencionadamente, con el fin de acentuar la diferencia entre las ejecuciones 
de las diferentes maneras se llego a la conclusion de que como era de esperarse en la ejecucion realizada de manera secuencial, lo que se 
pudo observar es que tardo un tiempo de 49.08s, mientras que cuando se implemento de manera "concurrente" mediante ThreadPool la ejecucion 
tardo 53.01s, esto sucede debido a que en python debido a las implicaciones de GIL no se pueden ejecutar hilos de manera concurrente 
realmente, ya que si bien si se crean dichos hilos, estos ejecutan de manera secuencial, por lo que esa diferencia de tiempo negativa se
debe al overhead de cambio de contexto minimo entre los hilos. Por ultimo pudo observarse que en la ejecucion realizada con ProcessPool 
el tiempo se redujo significativamente a 25.07s debido a que se crearon nuevos procesos, los cuales no esan limitados por el python, una
aclaracion importante es que esta ejecucion se realizo en una maquina particular y no en google collab, ya que debido a las limitaciones 
de dicha aplicacion no es posible ejecutar varios procesos a la vez.
'''