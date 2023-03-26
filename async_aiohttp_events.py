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
from multiproc_authors import main_multiproc


# Need to handle errors
async def get_author_events_without_data(author: Author, asession) -> List:
    author_link = author.link
    await asyncio.sleep(0.5)
    try:
        async with asession.get(author_link) as resp:
            apage = await resp.text()
    except Exception as exc:
        print(f"Exception occured: {exc}\n{PROC_STOP_MSG}")
        sys.exit()

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


async def get_event_data_async(event, asession, author) -> Dict[str, str]:
    """ Return dict containing event data: name, dates,
        place, link.
    """
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
        event_dates_block = event_soup.find("span", class_="dates-string inline-block")
        event_dates = " ".join([text_handler(date.text) for date in event_dates_block])
    except (AttributeError, TypeError):
        event_dates = NA_SIGN

    try:
        event_place = event_soup.find("div",
            class_="translation-editor-view").text
    except AttributeError:
        try:
            event_place = event_soup.find("div",
            class_="translation-auto-view").text
        except AttributeError:
            try:
                event_place = event_soup.find("div",
            class_="translation-undefined-view").text
            except AttributeError:
                event_place = NA_SIGN

    event_place = text_handler(event_place)

    event_name_dict = {'event_name': event_name}
    if event_name == NA_SIGN:
        print("Empty event")
        return None
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
        task = asyncio.create_task(get_event_data_async(event, asession, author))
        tasks.append(task)
    events_with_data = await asyncio.gather(*tasks)
    len_before = len(events_with_data)
    events_with_data_cleaned = [event for event in events_with_data if event]
    len_after = len(events_with_data_cleaned)
    if len_before != len_after:
        empty_count = len_before - len_after
        print(f"===INFO=== {author.name_en!r} has {len_before - len_after} empty event{'s' if empty_count > 1 else ''}")

    author.events = events_with_data_cleaned
    print(f"Author {author.name_en!r} is ready")
    return author


async def main(all_authors_list) -> List[Author]:
    headers = get_headers(fake_user_agent=True)
    print("\nStart collecting of authors' events...")

    async with aiohttp.ClientSession(headers=headers) as asession:
        tasks = [get_author_with_full_events_async(author, asession) for author in all_authors_list]
        all_authors_w_events = await asyncio.gather(*tasks)

    print("Collecting of authors' events finished successfully")
    return all_authors_w_events


def save_content_to_json(all_authors_w_events: List[Author],
                         filename: str = None) -> None:
    """ Get author as object of class Author, then convert it to the dict
        and add it to the list of all authors.
        Finally, increased list of all authors save to the json file. """

    if filename is None:
        date_time = datetime.now().strftime("%Y.%m.%d__%H:%M")
        filename = f"MAsync_{date_time}"
    print(f"\nStart saving authors to file \'{filename}.json\'...")

    all_authors_as_dicts__list = []
    count_authors = len(all_authors_w_events)
    for author in all_authors_w_events:
        author_in_dict = author.author_obj_into_dict()
        all_authors_as_dicts__list.append(author_in_dict)
    with open(f"{filename}.json", "w", encoding='utf-8') as json_file:
        json.dump(all_authors_as_dicts__list, json_file, indent=4, ensure_ascii=False)

    print("Saving authors to JSON file finished")
    print(f"[INFO] {count_authors} author{'s are' if count_authors > 1 else ' is'} added to file \'{filename}.json\'")


if __name__ == "__main__":
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    print("Process started =>")
    start = datetime.now()

    ### 1 Get authors from site (multiprocessing)
    all_authors_list = main_multiproc()
    ### 2 Get full authors' content (async)
    all_authors_w_events = asyncio.run(main(all_authors_list))
    ### 3 Save content
    save_content_to_json(all_authors_w_events)

    print("\n=> Process finished successfully!")
    print(f"Async time: {datetime.now() - start}")

