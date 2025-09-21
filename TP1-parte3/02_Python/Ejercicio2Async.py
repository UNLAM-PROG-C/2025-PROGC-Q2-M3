'''
Ejercicio propuesto (Async/Await): Elige un lenguaje (ej: Python o C#) y construye una pequeña aplicación que realice múltiples peticiones HTTP a diferentes URLs de forma asíncrona usando async/await. Mide el tiempo total comparándolo contra una versión sincrónica que haga las peticiones secuencialmente. ¿Cuánto mejora el tiempo? Analiza también el uso de CPU y threads en cada caso. Opcional: Si manejas varios lenguajes, implementa el mismo escenario en Python, C# o Java (usando CompletableFuture) y compara las diferencias de sintaxis y facilidad.
'''

import aiohttp
import asyncio
import time

async def fetch_async(session, url):
    print(f"(async) Ingresando {url}")
    async with session.get(url) as respuesta:
        return await respuesta.text()

async def main_async():
    inicio = time.time()
    async with aiohttp.ClientSession() as session:
        tareas = [fetch_async(session, url) for url in urls]
        resultados = await asyncio.gather(*tareas)
    fin = time.time()
    print(f"Tiempo total (asincrónico): {fin - inicio:.2f} segundos")

    proceso = psutil.Process(os.getpid())
    print(f"Uso de CPU (%): {proceso.cpu_percent(interval=1)}\n")

# En Colab usamos await directamente
await main_async()