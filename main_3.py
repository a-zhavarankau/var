import sys
import pyppeteer.errors
import requests
import requests_html
import json
import fake_useragent
import time
from datetime import datetime
from requests_html import HTMLSession
from typing import List, Dict, Set, Tuple, Any
from random import randint
from parsing_tools_3 import get_authors_by_letter, get_author_events, get_event_data, Author
from config import PROC_STOP_MSG, URL, NA_SIGN


def timer(func):
    def wrap(*args, **kwargs):
        start = datetime.now()
        res = func(*args, **kwargs)
        time = datetime.now() - start
        print(f"[Timer information] Function {func.__name__!r} executed in time: {str(time)[:7]}")
        return res
    return wrap


def get_headers(fake_user_agent=False) -> Dict[str, str]:
    """ Returns headers containing fake useragent if agrument 'fake_user_agent'=True
        (default=False), else original useragent.
    """
    fake_user = fake_useragent.UserAgent().random
    original_user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " \
                    "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
                  "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": fake_user if fake_user_agent else original_user,
    }
    return headers


def get_main_response_and_check_200(url: str, lang: str) -> Any:
    """ Take an url and return response object if response status is 200 [OK].
    """
    headers = get_headers(fake_user_agent=True)
    langs = {"en": "", "be": "/be", "ru": "/ru"}
    link = url + langs[lang]
    try:
        session = HTMLSession()
        response = session.get(link, headers=headers)
    except requests.exceptions.RequestException as reRE:
        print(f"[ERROR] {reRE}{PROC_STOP_MSG}")
        sys.exit()
    if response.status_code == 200:
        return response
    else:
        print(f"[ERROR] Response is not OK (status code is not 200). Check the URL.{PROC_STOP_MSG}")


def get_response_per_scroll(response: Any, lang: str) -> Any:
    """ Take the response and provide JS script during 'render()' function.
        Script performs (imitates) 'scrolls' amount per every script execution.
        'js_out' is script's output that contain new coordinate of scrolled page bottom
        and result ("1" - if the main page's bottom is reached, "0" - in other case).
        When "1", return response object.
    """
    language = {"en": "English", "be": "Belarusian", "ru": "Russian"}
    time.sleep(randint(1, 2))
    print(f"\nStart scrolling in {language[lang]}...")
    js_out = {'result': 0}
    counter = -1  # Started from '-1' to load first unscrolled page (usually from '0')
    scrolls = 5   # Amount of scrolls per script execution = per render()
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
            print(f"Scrolling {counter}: {js_out}")
        except pyppeteer.errors.TimeoutError as pyTE:
            print(f"[ERROR] {pyTE} In the 'render()' function set bigger volume to 'timeout=' (20 by default)."
                  f"{PROC_STOP_MSG}")
            sys.exit()
        except Exception as exc:
            print(f"[ERROR] {exc}")
        else:
            yield response


def show_dict_as_json(file):
    with open(file) as jf:
        json_data = json.load(jf)
    return json.dumps(json_data, indent=4, ensure_ascii=False)


def get_all_authors_list_lang(all_authors_list: List, response, lang: str) -> List[Author]:
    """ Add authors to the list of authors by specified language.
        If author already in list, add name in specified language to author's data.
        Return list of author objects collected by language.
    """
    for next_response in get_response_per_scroll(response, lang):
        authors_per_scroll = get_authors_by_letter(next_response, lang)
        for author in authors_per_scroll:
            is_author_in_list = False
            for author_in_all_authors in all_authors_list:
                if author_in_all_authors.link == author.link:
                    author_in_all_authors.__dict__[f"name_{lang}"] = author.__dict__[f"name_{lang}"]
                    # print(f'name_{lang} = {author.__dict__[f"name_{lang}"]}')
                    is_author_in_list = True
                    break
            if not is_author_in_list:
                all_authors_list.append(author)
                # print(f"Author not in list: {author.__dict__[f'name_{lang}']}")
    return all_authors_list


def check_missed_names(all_authors_list: List) -> None:
    """ Find authors without EN, BE or RU name. Open author's page by link
        and get name if exists, then change None to the name or "N/A (EN name)".
    """
    print(f"\nStart filling missed names...")
    headers = get_headers(fake_user_agent=True)
    session = requests_html.HTMLSession()
    langs = {"en": "", "be": "/be", "ru": "/ru"}
    count = 1
    for author in all_authors_list:
        if not all((author.name_en, author.name_be, author.name_ru)):
            for lang in ("en", "be", "ru"):
                if author.__dict__[f"name_{lang}"] is None:
                    author_link = author.link.replace("/names", f"{langs[lang]}/names")
                    print(author_link)
                    resp = session.get(url=author_link, headers=headers)
                    try:
                        author_name = resp.html.find("h1[class*='post-title translation-view']", first=True).text
                    except AttributeError:
                        author_name = f"{NA_SIGN} ({author.name_en})"
                    author.__dict__[f"name_{lang}"] = author_name
                    print(f'[INFO] Author #{count} added: name_{lang} = {author.__dict__[f"name_{lang}"]!r}')
            count += 1



def get_author_content():
    """ Prepare the whole content (author's data + events' data) to save.
    """
    print("[INFO] Process started =>")
    url = URL
    data = datetime.now().strftime("%d.%m.%Y")
    all_authors_list = []

    # for lang in ("en", "be", "ru"):
    #     response = get_main_response_and_check_200(url, lang)
    #     all_authors_list = get_all_authors_list_lang(all_authors_list, response, lang)

    a = 0

    # response = get_main_response_and_check_200(url, "en")
    # all_authors_list = get_all_authors_list_lang(all_authors_list, response, "en")
    # for i in all_authors_list[-3:]:
    #     print(i)
    #
    # response = get_main_response_and_check_200(url, "be")
    # all_authors_list = get_all_authors_list_lang(all_authors_list, response, "be")
    # for i in all_authors_list[-3:]:
    #     print(i)
    #
    #
    # response = get_main_response_and_check_200(url, "ru")
    # all_authors_list = get_all_authors_list_lang(all_authors_list, response, "ru")
    # for i in all_authors_list[-3:]:
    #     print(i)


    ### To EN file
    # response = get_main_response_and_check_200(url, "en")
    # all_authors_list = get_all_authors_list_lang(all_authors_list, response, "en")
    # for i in all_authors_list[-3:]:
    #     print(i)
    # all_authors_for_json = [i.author_obj_into_dict() for i in all_authors_list]
    # with open(f"LA_{data}_all_authors_list_en.json", "w", encoding='utf-8') as jf:
    #     json.dump(all_authors_for_json, jf, indent=4, ensure_ascii=False)
    # ### From EN file
    # with open(f"LA_{data}_all_authors_list_en.json") as jf:
    #     all_authors_from_json = json.load(jf)
    # all_authors_list = [author_dict_into_obj(i) for i in all_authors_from_json]

    # print(type(all_authors_list[0]), all_authors_list[0])

    # ### To BE file
    # response_be = get_main_response_and_check_200(url, "be")
    # all_authors_list = get_all_authors_list_lang(all_authors_list, response_be, "be")
    # for i in all_authors_list[-3:]:
    #     print(i)
    # all_authors_for_json = [i.author_obj_into_dict() for i in all_authors_list]
    # with open(f"LA_{data}_all_authors_list_be.json", "w", encoding='utf-8') as jf:
    #     json.dump(all_authors_for_json, jf, indent=4, ensure_ascii=False)
    # ### From BE file
    # with open(f"LA_{data}_all_authors_list_be.json") as jf:
    #     all_authors_from_json = json.load(jf)
    # all_authors_list = [author_dict_into_obj(i) for i in all_authors_from_json]

    # ### To RU file
    # response_ru = get_main_response_and_check_200(url, "ru")
    # all_authors_list = get_all_authors_list_lang(all_authors_list, response_ru, "ru")
    # for i in all_authors_list[-3:]:
    #     print(i)
    # all_authors_for_json = [i.author_obj_into_dict() for i in all_authors_list]
    # with open(f"LA_{data}_all_authors_list_ru.json", "w", encoding='utf-8') as jf:
    #     json.dump(all_authors_for_json, jf, indent=4, ensure_ascii=False)
    # ### From RU file
    # with open(f"LA_{data}_all_authors_list_ru.json") as jf:
    #     all_authors_from_json = json.load(jf)
    # all_authors_list = [author_dict_into_obj(i) for i in all_authors_from_json]


    # # ### To ALL_AUTHORS file
    # all_authors_for_json = [i.author_obj_into_dict() for i in all_authors_list]
    # with open(f"LA_{data}_all_authors_unchecked.json", "w", encoding='utf-8') as jf:
    #     json.dump(all_authors_for_json, jf, indent=4, ensure_ascii=False)

    ### From ALL_AUTHORS file
    # with open(f"LA_{data}_all_authors_unchecked.json") as jf:
    #     all_authors_from_json = json.load(jf)
    #     all_authors_list = [author_dict_into_obj(i) for i in all_authors_from_json]


    # Function fixes the issues with: NOVA, Шестая линия, Michael Veksler, Tasha Arlova, Leonid Shchemelev
    # check_missed_names(all_authors_list)

    # ### To ALL_AUTHORS_CHECKED file
    # all_authors_for_json = [i.author_obj_into_dict() for i in all_authors_list]
    # with open(f"LA_{data}_all_authors_checked.json", "w", encoding='utf-8') as jf:
    #     json.dump(all_authors_for_json, jf, indent=4, ensure_ascii=False)

    # ### From ALL_AUTHORS file
    # with open(f"LA_{data}_all_authors_checked.json") as jf:
    #     all_authors_from_json = json.load(jf)
    #     all_authors_list = [author_dict_into_obj(i) for i in all_authors_from_json]


    # authors_without_all_names = []
    # for author in all_authors_list:
    #     if not all((author.name_en, author.name_be, author.name_ru)):
    #         authors_without_all_names.append(author)
    #         print(f"{author.name_en} - {author.name_be} - {author.name_ru}")


    # ### To Authors_without_all_names file
    # all_authors_for_json = [i.author_obj_into_dict() for i in authors_without_all_names]
    # with open(f"LA_{data}_authors_without_all_names.json", "w", encoding='utf-8') as jf:
    #     json.dump(all_authors_for_json, jf, indent=4, ensure_ascii=False)

    # ### From Authors_without_all_names file
    # with open(f"LA_{data}_authors_without_all_names.json") as jf:
    #     authors_without_all_names_json = json.load(jf)
    #     authors_without_all_names = [author_dict_into_obj(i) for i in authors_without_all_names_json]
    #
    # print(len(authors_without_all_names))
    a = 0
    ## From ALL_AUTHORS_CHECKED file
    with open(f"LA_{data}_all_authors_checked.json") as jf:
        all_authors_from_json = json.load(jf)

    # Variable 'all_authors_list' contains all authors collected in 3 languages,
    # and their data except 'events'
    all_authors_list = [Author.author_dict_into_obj(i) for i in all_authors_from_json]

    count_authors = len(all_authors_list)
    print(f"[INFO] {count_authors} author{'s are' if count_authors > 1 else ' is'} collected from the site.")

    for author in all_authors_list:
        author_link = author.link
        headers = get_headers(fake_user_agent=True)
        author_events, session_2 = get_author_events(author_link, headers)
        for event in author_events:
            event_data = get_event_data(event, session_2, headers)
            author.events.append(event_data)
        yield author, count_authors


def save_content_to_json() -> None:
    """ Get all content about one author and add it to the list.
        At the end of all authors list converted to the json file. """
    date_time = datetime.now().strftime("%d.%m.%Y_%H-%M")
    all_authors_in_dict_list = []
    count = 0
    for author_and_amount in get_author_content():
        if count == 0: print(f"\nStart saving authors to file...")
        author, authors_amount = author_and_amount

        author_in_dict = author.author_obj_into_dict()
        all_authors_in_dict_list.append(author_in_dict)
        count += 1
        print(f"[INFO] {count}/{authors_amount} Author {author.name_en!r} executed")
        with open(f"LA_{date_time}.json", "w", encoding='utf-8') as json_file:
            json.dump(all_authors_in_dict_list, json_file, indent=4, ensure_ascii=False)


@timer
def mainthread():
    # get_author_content()
    save_content_to_json()


if __name__ == '__main__':
    mainthread()
    print("=== Process finished successfully! ===")