import asyncio

BASE_DELAY = 10

async def fetch_data(data_source):
    await asyncio.sleep(BASE_DELAY)
    return f"comunicación con {data_source} exitosa"

async def main():
    print("iniciando programa")
    result = await fetch_data("dispositivo E/S")
    print(f"resultado: {result}")
    print("programa completado")

if __name__ == "__main__":
    asyncio.run(main())
