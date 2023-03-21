import multiprocessing
import asyncio
import aiohttp
import csv
import json
import sys
import threading
import time
from datetime import datetime
import requests
import requests_html
import pyppeteer.errors
from requests_html import HTMLSession, AsyncHTMLSession
from random import randint
from typing import List, Dict, Tuple, Any, Generator
# from parsing_tools_3 import get_authors_by_letter, get_author_events, get_event_data, Author
from parsing_tools_3 import get_authors_by_letter, get_event_data, Author
from auxiliary_tools import get_headers, create_temp_file, create_temp_file_lang
from config import PROC_STOP_MSG, URL, NA_SIGN


lipavy_cviet = {
    "name_en": "Lipavy Cviet",
    "name_be": "Ліпавы цвет",
    "name_ru": "Липовый цвет",
    "occupation": "group",
    "link": "https://kalektar.org/names/xHYkVFaGa0N0jm8ko2Ol",
    "source": "https://kalektar.org",
    "events": [
        {
            "event_name": "Every Day. Art. Solidarity. Resistance",
            "event_dates": "March 24 – June 5, 2021",
            "event_place": "Mystetskyi Arsenal, Kyiv",
            "event_link": "https://kalektar.org/names/v9fo24NG7O02YE8kOYuJ"
        },
        {
            "event_name": "ZBOR. Движение беларусского искусства",
            "event_dates": "March 30 – May 5, 2016",
            "event_place": "ИЗОЛЯЦИЯ, Киев",
            "event_link": "https://kalektar.org/names/T8bXUaReHgBvFUGUIhGR"
        },
        {
            "event_name": "ZBOR. Constructing an Archive",
            "event_dates": "August 27 – October 7, 2015",
            "event_place": "Галерея Арсенал в Белостоке",
            "event_link": "https://kalektar.org/names/Ir4F5FKMZBztZVzHSCKR"
        }
    ]
}
# print(makeout['events'])


def get_authors_list():
    with open("TEMP_all_authors.json") as jf:
        list = json.load(jf)
        all_authors_list = [Author.author_dict_into_obj(i) for i in list]

    # authors_list = all_authors_list[261:262]
    authors_list = all_authors_list
    return authors_list


# Need to handle errors
async def get_author_events_without_data(author, asession) -> List:
    author_link = author.link
    # author_events = author.events
    headers = get_headers(fake_user_agent=True)
    try:
        aresponse = await asession.get(url=author_link, headers=headers)
    except Exception as exc:
        print(f"Exception occured: {exc}\n{PROC_STOP_MSG}")
        sys.exit()
    else:
        apage = requests_html.HTML(html=aresponse.text)
        events = apage.find("div[class*='cell-box cell-box-ref public event']")
        return events


def text_handler(text: str):
    """ Check text for unwanted symbol and change it.
        Example: "Text\ntranslation" -> "Text (translation)".
    """
    if "\n" in text:
        text = text.replace("\n", " (") + ")"
    return text


async def get_event_data_async(event, asession) -> Dict[str, str]:
    """ Return dict containing event data: name, dates,
        place, link.
    """
    headers = get_headers(fake_user_agent=True)
    event_token = event.find("a.post-link-box")[0].links
    event_link = "https://kalektar.org" + event_token.pop()

    aresponse = await asession.get(url=event_link, headers=headers)
    apage = requests_html.HTML(html=aresponse.text)
    try:
        event_name = apage.find("h1[class*='post-title translation-view']", first=True).text
        event_name = text_handler(event_name)
    except AttributeError:
        event_name = NA_SIGN

    try:
        event_dates_block = apage.find("span[class*='dates-string inline-block']")
        event_dates = "".join([date.text for date in event_dates_block])
    except AttributeError:
        event_dates = NA_SIGN

    try:
        event_place = apage.find("div.translation-editor-view", first=True).text
    except AttributeError:
        try:
            event_place = apage.find("div.translation-auto-view", first=True).text
        except AttributeError:
            try:
                event_place = apage.find("div.translation-undefined-view", first=True).text
            except AttributeError:
                event_place = NA_SIGN

    event_name_dict = {'event_name': event_name}
    event_dates_dict = {'event_dates': event_dates}
    event_place = event_place.replace("\xa0\xa0\xa0", ";")
    event_place_dict = {'event_place': event_place}
    event_link_dict = {'event_link': event_link}
    event_dict = event_name_dict | event_dates_dict | event_place_dict | event_link_dict
    return event_dict


async def get_author_with_full_events_async(author, asession):
    author_events_without_data: List = await get_author_events_without_data(author, asession)
    for event in author_events_without_data:
        event_data = await get_event_data_async(event, asession)
        author.events.append(event_data)

    # async for event in iter(author_events_without_data):
    #     event_data = await get_event_data_async(event, asession)
    #     author.events.append(event_data)

    # a_session_2 = AsyncHTMLSession()
    # tasks_2 = [lambda event=event: get_event_data_async(event, asession) for event in author_events_without_data]
    # author.events = asession.run(*tasks_2)
    # print(author.events)

    print(f"Author {author.name_en} is ready")
    return author


def main() -> List[Author]:
    all_authors_list = get_authors_list()

    a_session = AsyncHTMLSession()
    tasks = [lambda author=author: get_author_with_full_events_async(author, a_session) for author in all_authors_list]
    all_authors_w_events = a_session.run(*tasks)

    return all_authors_w_events


if __name__ == "__main__":
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    print("Process started =>")
    start = datetime.now()
    # all_authors_w_events = asyncio.run(main())
    all_authors_w_events = main()
    authors_count = len(all_authors_w_events)
    print(f"\nIn 'all_authors_w_events' {authors_count} authors.")
    for author in all_authors_w_events:
        print(f"Author {author.name_en!r} with events: {author.events}")

#     save_content_to_json(all_authors_w_events)
    print(f"Async time: {datetime.now() - start}")

