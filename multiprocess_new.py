import multiprocessing
import asyncio
import csv
import json
import sys
import threading
import time
from datetime import datetime
import requests
import requests_html
import pyppeteer.errors
from requests_html import HTMLSession
from random import randint
from typing import List, Dict, Tuple, Any, Generator
from parsing_tools_3 import get_authors_by_letter, get_author_events, get_event_data, Author
from auxiliary_tools import get_headers, create_temp_file, create_temp_file_lang
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
    print(f"\nStart scrolling in {language[lang]}...")
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


def get_all_authors_list_lang(lang: str) -> List[Author]:
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


def create_all_authors_list(all_authors_dict: Dict[str, Author]):
    """ Create all_authors_list and fill it with names in
        EN/BE/RU languages.
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


def check_missed_names(all_authors_list: List) -> None:
    """ Find authors without EN, BE or RU name. Open author's page by link
        and get name if exists, then change None to the name or "N/A (EN name)".
    """
    print("\nStart filling missed names...")
    headers = get_headers(fake_user_agent=True)
    session = requests_html.HTMLSession()
    langs = {"en": "", "be": "/be", "ru": "/ru"}
    count = 1
    for author in all_authors_list:
        if not all((author.name_en, author.name_be, author.name_ru)):
            for lang in ("en", "be", "ru"):
                if author.__dict__[f"name_{lang}"] is None:
                    author_link = author.link.replace("/names", f"{langs[lang]}/names")
                    resp = session.get(url=author_link, headers=headers)
                    try:
                        author_name = resp.html.find("h1[class*='post-title translation-view']", first=True).text
                    except AttributeError:
                        author_name = f"{NA_SIGN} ({author.name_en})"
                    author.__dict__[f"name_{lang}"] = author_name
                    print(f'[INFO] Author #{count} added: name_{lang} = {author.__dict__[f"name_{lang}"]!r}')
            count += 1


def handle_all_authors_lists(results: List[Tuple[List, str]]):
    """ Create final all_authors_list (without events)
        from all lists of authors in EN/BE/RU.
    """
    all_authors_dict = {}
    # Create a dict = {'language': 'list of authors'}.
    # Need this to keep parsing process under control.
    for data in results:
        all_authors_list_lang, lang = data
        all_authors_dict[lang] = all_authors_list_lang
        create_temp_file_lang(all_authors_list_lang, lang)

    # Get all_authors_list with all names in EN/BE/RU
    all_authors_list = create_all_authors_list(all_authors_dict)

    # Function fixes the issues with: NOVA, Шестая линия, Michael Veksler, Tasha Arlova, etc.
    check_missed_names(all_authors_list)
    create_temp_file(all_authors_list)

    count_authors = len(all_authors_list)
    msg_collected = f"{count_authors} author{'s are' if count_authors > 1 else ' is'} collected from the site."
    print(f"[INFO] {msg_collected}")
    return all_authors_list, count_authors


def start_multiproc_authors_collection():
    """ Start authors collection in 3 languages simultaneously.
        Used 'multiprocessing' module.
    """
    with multiprocessing.Pool(processes=3) as pool:
        all_authors_lists_and_langs = pool.map(get_all_authors_list_lang, ['en', 'be', 'ru'])
        pool.close()
        pool.join()

    print("Multiprocessing finished")
    all_authors_list = handle_all_authors_lists(all_authors_lists_and_langs)
    return all_authors_list


def add_events_to_author(author: Author) -> Author:
    """ Get an author without events and add all events to it.
        Return the author, ready to be saved.
    """
    author_link = author.link
    # Use fake headers to imitate real users
    headers = get_headers(fake_user_agent=True)
    time.sleep(1)
    author_events, session_2 = get_author_events(author_link, headers)
    for event in author_events:
        event_data = get_event_data(event, session_2, headers)
        author.events.append(event_data)
    print("[INFO] Author is ready: ", author)
    return author


def start_multiproc_events_collection(all_authors_list):
    """ Start authors collection in 3 languages simultaneously.
        Used 'multiprocessing' module.
    """
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()*3) as pool:
        all_new_authors = pool.map(add_events_to_author, [author for author in all_authors_list])
        pool.close()
        pool.join()

    print("Multiprocessing events finished")
    return all_new_authors


def save_content_to_json(all_new_authors, count_authors) -> None:
    """ Get author as object of class Author, then convert it to the dict
        and add it to the list of all authors.
        Finally, increased list of all authors save to the json file. """

    date_time = datetime.now().strftime("%Y.%m.%d__%H:%M")
    filename = f"MPLA_{date_time}.json"
    all_authors_as_dicts__list = []
    count = 0
    for author in all_new_authors:
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


def main():
    # all_authors_list, count_authors = start_multiproc_authors_collection()
    with open("TEMPooo_all_authors.json") as jf:
        list = json.load(jf)
        all_authors_list = [Author.author_dict_into_obj(i) for i in list]
        count_authors = len(all_authors_list)

    all_new_authors = start_multiproc_events_collection(all_authors_list[-20:])

    save_content_to_json(all_new_authors, count_authors)
        # yield author, count_authors     # Author is full and ready to store
    # print(all_authors_list, count_authors)


if __name__ == "__main__":
    start = datetime.now()
    main()
    print(f"Mutliprocessing w/Pool time: {datetime.now() - start}")


