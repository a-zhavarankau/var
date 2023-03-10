import sys
import asyncio
import aiohttp
import time
import requests
from random import randint
import pyppeteer.errors
import requests_html
from requests_html import HTMLSession
from typing import List, Dict, Tuple, Any, Generator
from parsing_tools_3 import get_authors_by_letter, get_author_events, get_event_data, Author
from datetime import datetime
from auxiliary_tools import timer, get_headers
from aiohttp.client_exceptions import ClientConnectorError
from config import PROC_STOP_MSG, URL, NA_SIGN


async def get_data(session, url):
    try:
        async with session.get(url) as response:
            try:
                response.status == 200
            except Exception as e:
                print("Response status is not OK (200)", e)
                sys.exit()
            else:
                print("Resp is got")
                return response
                # return await response.text()
                # return await response.text(encoding='utf-8')
    except aiohttp.client_exceptions.ClientConnectorError as e:
        print("Alarm!", e)


async def get_response_per_scroll(response: Any) -> Any:
    time.sleep(2)
    print(f"\nStart scrolling...")
    # response = response.text()
    time.sleep(3)
    js_out = {'result': 0}
    counter = -1
    scrolls = 5
    scroll_height = 300
    while js_out['result'] == 0:
        js_script_down = f'(function down() {{let y={counter}; for(let i={scrolls}*y;i<{scrolls}*(y+1);i++) ' \
                     f'{{if ((window.scrollY + window.innerHeight) >= document.body.scrollHeight) {{' \
                     f'return {{result: 1, coordinates: window.pageYOffset}}; }};' \
                     f'window.scrollTo(0, i*{scroll_height});' \
                     f'}};' \
                     f'return {{result: 0, coordinates: window.pageYOffset}}' \
                     f'}})()'
        counter += 1
        try:
            js_out = await response.html.arender(timeout=30, sleep=2, script=js_script_down)
            print(f"Scrolling {counter}: {js_out}")
        except pyppeteer.errors.TimeoutError as pyTE:
            pyTE_msg = f"{pyTE}\nIn the 'render()' function, you should set bigger volume to 'timeout=' (20 seconds by default).{PROC_STOP_MSG}"
            print(f"[ERROR] {pyTE_msg}")
            sys.exit()
        except Exception as exc:
            print(f"[ERROR] {exc}")
        else:
            # yield response
            print(response)


async def main():
    headers = get_headers(fake_user_agent=True)

    async with aiohttp.ClientSession(headers=headers) as session:
        urls = [
            'https://kalektar.org',
            # 'https://kalektar.org/be',
            # 'https://kalektar.org/ru'
        ]

        tasks = [asyncio.create_task(get_data(session, url)) for url in urls]
        results = await asyncio.gather(*tasks)
        for result_resp in results:
            print(result_resp, "\n", "*"*100, "\n")
            await get_response_per_scroll(result_resp)

asyncio.run(main())







# async def get_data2(session, url):
#     resp = await session.get(url)
#     return resp.status
