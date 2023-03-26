import multiprocessing
import asyncio
import aiohttp
import csv
import json
import sys
import time
from datetime import datetime
from bs4 import BeautifulSoup as bs
import requests
import requests_html
import pyppeteer.errors
from requests_html import HTMLSession
from random import randint
from typing import List, Dict, Tuple, Any, Generator
from parsing_tools_3 import get_authors_by_letter, get_author_events, get_event_data, Author
from auxiliary_tools_4 import get_headers, create_temp_file, create_temp_file_lang
from config import PROC_STOP_MSG, URL, NA_SIGN


def get_main_response_and_check_200(url: str, lang: str) -> Any:
    headers = get_headers(fake_user_agent=True)
    langs = {"en": "", "be": "/be", "ru": "/ru"}
    link = url + langs[lang]
    session = HTMLSession()
    response = session.get(link, headers=headers)
    if response.status_code == 200:
        return response
    print(f"[ERROR] Response is not OK (status code is not 200). Check the URL.{PROC_STOP_MSG}")


def get_response_per_scroll(response: Any, lang: str) -> Any:
    language = {"en": "English", "be": "Belarusian", "ru": "Russian"}
    time.sleep(randint(1, 2))
    print(f"Start scrolling in {language[lang]}...")
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
            js_out = response.html.render(timeout=30, sleep=2, script=js_script_down)
            print(f"{lang.upper()!r} Scrolling {counter}: {js_out}")
        except pyppeteer.errors.TimeoutError as pyTE:
            pyTE_msg = f"{pyTE}\nIn the 'render()' function, you should set bigger volume to 'timeout=' (20 seconds by default).{PROC_STOP_MSG}"
            print(f"[ERROR] {pyTE_msg}")
            sys.exit()
        except Exception as exc:
            print(f"888 [ERROR] {exc}")
            sys.exit()
        else:
            yield response


def get_authors_by_lang(lang: str) -> List[Author]:
    """ Get responses per scroll and create list of all
        authors in specified language.
    """
    url = URL
    response = get_main_response_and_check_200(url, lang)
    print(f"{lang.upper()!r}", response)
    all_authors_list_lang = []
    for next_response in get_response_per_scroll(response, lang):
        authors_per_scroll = get_authors_by_letter(next_response, lang)
        for author in authors_per_scroll:
            if author not in all_authors_list_lang:
                all_authors_list_lang.append(author)
    return all_authors_list_lang, lang


def create_all_authors_list(all_authors_dict: Dict[str, List[Author]]) -> List[Author]:
    """ Create list of all authors from dict of authors lists
        in different languages (separately) and fill it
        with names in EN/BE/RU languages from dict of authors lists.
    """
    all_authors_list = []
    for lang in all_authors_dict:
        for author_lang in all_authors_dict[lang]:
            is_author_in_list = False
            for author in all_authors_list:
                if author_lang == author:
                    author.__dict__[f"name_{lang}"] = author_lang.__dict__[f"name_{lang}"]
                    is_author_in_list = True
                    break
            if not is_author_in_list:
                all_authors_list.append(author_lang)
    return all_authors_list


def text_handler(text: str):
    """ Check text for unwanted symbol and change it.
        Example: "Text\ntranslation" -> "Text (translation)".
    """
    text = text.strip("\n ")
    if "\n" in text:
        text = text.replace("\n", " (") + ")"
    return text


async def check_author_names_async(author: Author) -> None:
    """ Find authors without EN, BE or RU name (for ex.: NOVA, Шестая линия,
        Michael Veksler, Tasha Arlova). Open author's page by link and get name
        if exists, then change None to the name or "N/A (EN name)".
    """
    langs = {"en": "", "be": "/be", "ru": "/ru"}
    headers = get_headers(fake_user_agent=True)
    if not all((author.name_en, author.name_be, author.name_ru)):
        for lang in ("en", "be", "ru"):
            if author.__dict__[f"name_{lang}"] is None:
                author_link = author.link.replace("/names", f"{langs[lang]}/names")
                async with aiohttp.ClientSession(headers=headers) as asession:
                    async with asession.get(author_link) as resp:
                        author_apage = await resp.text()
                        author_soup = bs(author_apage, 'lxml')
                try:
                    author_name = author_soup.find("h1", class_="post-title translation-view").text
                    author_name = text_handler(author_name)
                except AttributeError:
                    author_name = f"{NA_SIGN} ({author.name_en})"
                author.__dict__[f"name_{lang}"] = author_name
                print(f'[INFO] Author <{author.name_en}> added: name_{lang} = {author.__dict__[f"name_{lang}"]!r}')


async def check_missed_names_async(all_authors_list: List[Author]) -> None:
    """ Start async function that adds missed names in EN/BE/RU to author.
    """
    print("\nStart filling missed names...")
    tasks = [check_author_names_async(author) for author in all_authors_list]
    await asyncio.gather(*tasks)
    print("Filling missed names finished successfully")


def get_multiproc_authors_by_langs() -> List[Tuple[List[Author], str]]:
    """ Start authors collection in 3 languages simultaneously.
        Used 'multiprocessing' module.
    """
    print("\nStart collecting authors without events (multiprocessing)...")
    with multiprocessing.Pool(processes=3) as pool:
        authors_lists_by_langs = pool.map(get_authors_by_lang, ['en', 'be', 'ru'])
        pool.close()
        pool.join()

    print("Multiprocessing finished successfully")
    return authors_lists_by_langs


def put_multiproc_authors_in_dict(authors_lists_by_langs):
    """ Create a dict = {'language': 'list of authors'}.
        We need this function to keep parsing process under control.
    """
    authors_dict = {}
    for data in authors_lists_by_langs:
        authors_list_by_lang, lang = data
        authors_dict[lang] = authors_list_by_lang
    return authors_dict


def main_multiproc():
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."

    # Get dict of 3 lists of authors in EN/BE/RU
    authors_lists_by_langs = get_multiproc_authors_by_langs()
    # Put authors lists in dict = {'language': 'list of authors'}
    authors_dict = put_multiproc_authors_in_dict(authors_lists_by_langs)
    # Get all_authors_list with all names in EN/BE/RU
    all_authors_list = create_all_authors_list(authors_dict)
    create_temp_file(all_authors_list)

    # with open("TEMP_all_authors_not_all_names.json") as jf:
    #     authors_list = json.load(jf)
    #     all_authors_list = [Author.author_dict_into_obj(i) for i in authors_list]

    asyncio.run(check_missed_names_async(all_authors_list))

    count_authors = len(all_authors_list)
    msg_collected = f"{count_authors} author{'s are' if count_authors > 1 else ' is'} collected from the site."
    print(f"[INFO] {msg_collected}")

    return all_authors_list


# if __name__ == "__main__":
#     print("Module 'Multiproc_authors' has started")
#     start = datetime.now()
#     all_authors_list = main_multiproc()
#
#     save_content_to_json(all_authors_list)
#     print(f"Mutliprocessing w/Pool time: {datetime.now() - start}")


