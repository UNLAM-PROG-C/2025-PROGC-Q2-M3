import requests
import time
import threading, psutil, os

urls = [
    "https://www.velez.com.ar",
    "https://www.promiedos.com.ar",
    "https://www.github.com"
]

def fetch_sync(url):
    print(f"(sync) Ingresando {url}")
    respuesta = requests.get(url)
    return respuesta.text[:50]

def main_sync():
    inicio = time.time()
    for url in urls:
        fetch_sync(url)
    fin = time.time()
    print(f"Tiempo total (sincrónico): {fin - inicio:.2f} segundos")

    proceso = psutil.Process(os.getpid())
    print(f"Uso de CPU (%): {proceso.cpu_percent(interval=1)}\n")

# Ejecutamos la versión sincrónica
main_sync()


'''
La versión sincrónica realiza las peticiones de una en una, bloqueando el hilo principal mientras espera la respuesta de cada servidor. Por ello, el tiempo total es aproximadamente la suma de los tiempos de cada request.

La versión asincrónica lanza todas las peticiones casi simultáneamente mediante async/await. El tiempo total se aproxima al de la petición más lenta, lo que demuestra la eficiencia de la asincronía para operaciones I/O-bound.

En ambos casos la ejecución se lleva a cabo por un hilo principal. La diferencia es que en la versión sincrónica ese hilo se bloquea y en la asincrónica no se bloquea y realiza tareas concurrentemente. Es decir, puede altnernar entre varias tareas sin bloquearse.

En cuanto al uso de CPU lo vemos bajo en ambos casos. Esto entendemos que es debido a que en sincrónico como asincrónico esta realizando tareas de I/O, no procesamiento intensivo de CPU.
'''