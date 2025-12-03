import asyncio
import random
import threading

DELAY_BASE = 0.1
DELAY_MIN_VAR = 0.1
DELAY_MAX_VAR = 0.8
RANGE_INCLUSIVE = 1

START_TASK_1 = 1
END_TASK_1 = 10
START_TASK_2 = 11
END_TASK_2 = 20 
START_TASK_3 = 21
END_TASK_3 = 30

async def show_numbers(task_name, start, end):
    for number in range(start, end + RANGE_INCLUSIVE):
        delay = DELAY_BASE + random.uniform(DELAY_MIN_VAR, DELAY_MAX_VAR)
        await asyncio.sleep(delay)
        thread_id = threading.get_ident()
        print(f"{task_name}: {number} [thread ID: {thread_id}]")
    
async def main():
    task1 = asyncio.create_task(
        show_numbers("task 1", START_TASK_1, END_TASK_1)
    )
    
    task2 = asyncio.create_task(
        show_numbers("task 2", START_TASK_2, END_TASK_2)
    )
    
    task3 = asyncio.create_task(
        show_numbers("task 3", START_TASK_3, END_TASK_3)
    )
    
    try:
        await asyncio.gather(task1, task2, task3)
        print("todas las tareas completadas")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    print("iniciando programa")
    asyncio.run(main())
    print("\nprograma completado")