import multiprocessing
import asyncio
import aiohttp
import csv
import json
import sys
import threading
import time
from bs4 import BeautifulSoup as bs
import lxml
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

    # authors_list = all_authors_list[261:272]
    authors_list = all_authors_list
    return authors_list


# Need to handle errors
async def get_author_events_without_data(author, asession) -> List:
    author_link = author.link
    await asyncio.sleep(0.5)
    headers = get_headers(fake_user_agent=True)
    try:
        async with asession.get(author_link) as resp:
            apage = await resp.text()
    except Exception as exc:
        print(f"Exception occured: {exc}\n{PROC_STOP_MSG}")
        sys.exit()
    else:
        soup = bs(apage, 'lxml')
        events = soup.findAll("div", class_="cell-box cell-box-ref public event")
        return events


def text_handler(text: str):
    """ Check text for unwanted symbol and change it.
        Example: "Text\ntranslation" -> "Text (translation)".
    """
    text = text.strip("\n ")
    if "\n" in text:
        text = text.replace("\n", " (") + ")"
    return text


async def get_event_data_async(event, asession) -> Dict[str, str]:
    """ Return dict containing event data: name, dates,
        place, link.
    """
    headers = get_headers(fake_user_agent=True)
    event_token = event.find("a", class_="post-link-box").get("href")
    event_link = "https://kalektar.org" + event_token

    async with asession.get(event_link) as resp:
        event_apage = await resp.text()
        event_soup = bs(event_apage, 'lxml')
    try:
        event_name = event_soup.find("h1", class_="post-title translation-view").text
        event_name = text_handler(event_name)
    except AttributeError:
        event_name = NA_SIGN

    try:
        event_dates_block = event_soup.find("span",class_="dates-string inline-block")
        event_dates = " ".join([text_handler(date.text) for date in event_dates_block])
    except (AttributeError, TypeError):
        event_dates = NA_SIGN

    try:
        event_place = event_soup.find("div", class_="translation-editor-view").text
    except AttributeError:
        try:
            event_place = event_soup.find("div", class_="translation-auto-view").text
        except AttributeError:
            try:
                event_place = event_soup.find("div", class_="translation-undefined-view").text
            except AttributeError:
                event_place = NA_SIGN
    event_place = text_handler(event_place)

    event_name_dict = {'event_name': event_name}
    event_dates_dict = {'event_dates': event_dates}
    event_place = event_place.replace("\xa0\xa0\xa0", ";")
    event_place_dict = {'event_place': event_place}
    event_link_dict = {'event_link': event_link}
    event_dict = event_name_dict | event_dates_dict | event_place_dict | event_link_dict
    return event_dict


async def get_author_with_full_events_async(author, asession):
    author_events_without_data: List = await get_author_events_without_data(author, asession)

    tasks = []
    for event in author_events_without_data:
        task = asyncio.create_task(get_event_data_async(event, asession))
        tasks.append(task)
    events_with_data = await asyncio.gather(*tasks)
    author.events = events_with_data

    print(f"Author {author.name_en} is ready")
    return author


async def main() -> List[Author]:
    all_authors_list = get_authors_list()
    headers = get_headers(fake_user_agent=True)

    async with aiohttp.ClientSession(headers=headers) as asession:
        tasks = [get_author_with_full_events_async(author, asession) for author in all_authors_list]
        all_authors_w_events = await asyncio.gather(*tasks)

    return all_authors_w_events


def save_content_to_json(all_authors_w_events: List[Author]) -> None:
    """ Get author as object of class Author, then convert it to the dict
        and add it to the list of all authors.
        Finally, increased list of all authors save to the json file. """

    date_time = datetime.now().strftime("%Y.%m.%d__%H:%M")
    filename = f"M_aiohttp_{date_time}.json"
    all_authors_as_dicts__list = []
    count_authors = len(all_authors_w_events)
    count = 0
    for author in all_authors_w_events:
        if count == 0:
            print(f"\nStart saving authors to file {filename!r}...")
            time.sleep(3)

        author_in_dict = author.author_obj_into_dict()
        all_authors_as_dicts__list.append(author_in_dict)
        count += 1
        print(f"[INFO] {count}/{count_authors} Author {author.name_en!r} executed")
        with open(filename, "w", encoding='utf-8') as json_file:
            json.dump(all_authors_as_dicts__list, json_file, indent=4, ensure_ascii=False)

    print(f"{count_authors} author{'s are' if count_authors > 1 else ' is'} added to the {filename!r}.")


if __name__ == "__main__":
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    print("Process started =>")
    start = datetime.now()
    all_authors_w_events = asyncio.run(main())
    authors_count = len(all_authors_w_events)
    print(f"\nIn 'all_authors_w_events' {authors_count} authors.")
    for author in all_authors_w_events:
        print(f"Author {author.name_en!r} with events: {author.events}")

    save_content_to_json(all_authors_w_events)
    print(f"Async time: {datetime.now() - start}")

