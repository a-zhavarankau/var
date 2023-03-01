import asyncio
import aiohttp
# import requests
from typing import Dict
from datetime import datetime
from auxiliary_tools import timer, get_headers
from aiohttp.client_exceptions import ClientConnectorError


async def get_data(session, url):
    try:
        async with session.get(url) as response:
            try:
                response.status == 200
            except Exception as e:
                print("Response status is not OK (200)", e)
            else:
                return await response.read()
    except aiohttp.client_exceptions.ClientConnectorError as e:
        print("Alarm!", e)


async def get_data2(session, url):
    resp = await session.get(url)
    return resp.status


async def main():
    headers = get_headers(fake_user_agent=True)
    async with aiohttp.ClientSession(headers=headers) as session:
        urls = [
            'https://kalektar.org',
            'https://kalektar.org/be',
            'https://kalektar.org/ru'
        ]

        tasks = [asyncio.create_task(get_data(session, url)) for url in urls]
        results = await asyncio.gather(*tasks)
        for result in results:
            print(result, "\n", "*"*100, "\n")

asyncio.run(main())