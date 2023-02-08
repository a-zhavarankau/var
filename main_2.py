import sys
import pyppeteer.errors
import requests
import requests_html
import json
import fake_useragent
from requests_html import HTMLSession
from datetime import datetime
from parsing_tools import get_authors_by_letter, get_author_events, get_event_data
import time
from random import randint
from config import PROC_STOP_MSG, URL, NA_SIGN


def timer(func):
    def wrap(*args, **kwargs):
        start = datetime.now()
        res = func(*args, **kwargs)
        time = datetime.now() - start
        print(f"[Timer information] Function {func.__name__!r} executed in time: {time}")
        return res
    return wrap


def get_headers(fake_user_agent=False):
    """ Returns headers containing fake useragent if agrument 'fake_user_agent'=True
        (default=False), else original useragent
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


def get_main_response_and_check_200(url):
    headers = get_headers(fake_user_agent=True)
    try:
        session = HTMLSession()
        response = session.get(url, headers=headers)
    except requests.exceptions.RequestException as reRE:
        print(f"[ERROR] {reRE}{PROC_STOP_MSG}")
        sys.exit()
    if response.status_code == 200:
        return response
    else:
        print(f"[ERROR] Response is not OK (status code is not 200). Check the URL.{PROC_STOP_MSG}")


def get_response_per_scroll(response, lang):
    """ Take the main response and provide JS script during 'render()' function.
        Script performs (imitates) 'scrolls' amount per every script execution.
        'js_out' is script's output that contain new coordinate of scrolled page bottom
        and result ("1" - if the main page's bottom is reached, "0" - in other case). """
    language = {"en": "English", "be": "Belarusian", "ru": "Russian"}
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
            # time.sleep(randint(1, 3))
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

def get_all_authors_dict(all_authors_dict, response, lang):
    """ Return all authors from English url """
    gen = get_response_per_scroll(response, lang)
    while True:
        try:
            next_response = next(gen)
        except StopIteration:
            break
        authors_per_scroll = get_authors_by_letter(next_response)
        for author in authors_per_scroll:
            author_link = tuple(author)[0]
            if author_link not in all_authors_dict:
                all_authors_dict.update(author)
    return all_authors_dict

def change_order_in_author_data(author_from_dict):
        key_order = ('name_en', 'name_be', 'name_ru', 'occupation', 'link', 'source')
        new_author_from_dict = dict((k, author_from_dict.get(k, NA_SIGN)) for k in key_order)
        return new_author_from_dict

def add_name_be_ru_to_all_authors_dict(all_authors_dict, response, lang):
    """ Add names in Belarusian and Russian to all authors' dict from English url.
        If
    """
    count = 0
    new_name_field = f"name_{lang}"
    for next_response in get_response_per_scroll(response, lang):
        authors_per_scroll = get_authors_by_letter(next_response)
        count += 1
        # if count == 2:
        #     print(2)
        for author in authors_per_scroll:
            # is_author_in_all_authors = False
            author_link = tuple(author)[0]
            author_data = [v for _, v in author.items()][0]
            if author_link in all_authors_dict:
                # is_author_in_all_authors = True
                author_from_dict_data = all_authors_dict[author_link]
                if new_name_field not in author_from_dict_data:
                    author_name = author_data["name_en"] or NA_SIGN
                    author_from_dict_data[new_name_field] = author_name
                if lang == "ru":
                    dict_author_ordered = change_order_in_author_data(author_from_dict_data)
                    all_authors_dict[author_link] = dict_author_ordered
            else:
                all_authors_dict.update(author)
            # if not is_author_in_all_authors:
                print(f"Author not in dict: {author_link} ({author_data['name_en']})")
    return all_authors_dict

def recheck_all_authors_dict(all_authors_dict):
    langs = {"en": "", "be": "/be", "ru": "/ru"}
    count = 0
    for author in all_authors_dict:
        author_data = all_authors_dict[author]
        for lang in langs:
            if author_data.get("name_" + lang) and not author_data["name_" + lang] == "N/A":
                continue
            count += 1
            print(count)
            for lang in langs:
                link = author_data["link"][:-27] + langs[lang] + author_data["link"][-27:]
                session = requests_html.HTMLSession()
                resp = session.get(link)
                try:
                    name = resp.html.find("h1.post-title", first=True).text
                    if "\n" in name:
                        name = name.replace("\n", " (") + ")"
                except AttributeError:
                    name = "N_A"
                print(name)
                author_data["name_" + lang] = name
            break
        author_data_new = change_order_in_author_data(author_data)
        all_authors_dict[author] = author_data_new
    # return all_authors_dict

def get_author_content():
    """ Prepare the whole content (author's data + events' data) to save. """
    print("[INFO] Process started =>")
    url = URL
    response = get_main_response_and_check_200(url)
    response_be = get_main_response_and_check_200(url+"/be")
    response_ru = get_main_response_and_check_200(url+"/ru")

    # all_authors_list = []
    all_authors_dict = {}
    all_authors_list = get_all_authors_dict(all_authors_dict, response, "en")
    # with open("LA_08.02.2023_all_authors_dict_en.json", "w") as jf:
    #     json.dump(all_authors_list, jf, indent=4, ensure_ascii=False)
    # with open("LA_06.02.2023_all_authors_dict_en.json") as jf:
    #     all_authors_dict = json.load(jf)

    all_authors_dict = add_name_be_ru_to_all_authors_dict(all_authors_dict, response_be, "be")
    # with open("LA_06.02.2023_all_authors_dict_be.json", "w") as jf:
    #     json.dump(all_authors_dict, jf, indent=4, ensure_ascii=False)
    # with open("LA_06.02.2023_all_authors_dict_be.json") as jf:
    #     all_authors_dict = json.load(jf)
    #
    all_authors_dict = add_name_be_ru_to_all_authors_dict(all_authors_dict, response_ru, "ru")
    # with open("LA_06.02.2023_ru.json", "w") as jf:
    #     json.dump(all_authors_dict, jf, indent=4, ensure_ascii=False)

    with open("LA_08.02.2023_all_no_recheck.json", "w") as jf:
        json.dump(all_authors_dict, jf, indent=4, ensure_ascii=False)

    # with open("LA_06.02.2023_all.json") as jf:
    #     all_authors_dict = json.load(jf)

    # recheck_all_authors_dict(all_authors_dict)
    # Can't use it due to the issues with: NOVA, Шестая линия, Michael Veksler, Tasha Arlova

    # with open("LA_08.02.2023_all_with_recheck.json", "w") as jf:
    #     json.dump(all_authors_dict, jf, indent=4, ensure_ascii=False)

    count_authors = len(all_authors_dict)
    print(f"[INFO] {count_authors} author{'s are' if count_authors > 1 else ' is'} collected from the site.")

    for author in all_authors_list:
        author_data = (lambda auth: [v for _, v in auth.items()])(author)[0]
        author_name = author_data['name_en']

        headers = get_headers(fake_user_agent=True)
        author_events, session_2 = get_author_events(author_data, headers)
        author_data['events'] = []
        for event in author_events:
            event_data = get_event_data(event, session_2, headers)
            author_data['events'].append(event_data)
        yield (author, author_name, count_authors)


def save_content_to_json() -> None:
    """ Get all content about one author and add it to the list.
        At the end of all authors list converted to the json file. """
    date_time = datetime.now().strftime("%d-%m-%Y_%H-%M")
    # gen = get_author_content()
    final_content = []
    count = 0
    # while True:
    #     try:
    #         author_content, author_name, authors_amount = next(gen)
    #     except StopIteration:
    #         break
    for author_content_and_amount in get_author_content():
        author_content, author_name, authors_amount = author_content_and_amount
        final_content.append(author_content)
        count += 1
        print(f"[INFO] {count}/{authors_amount} Author {author_name!r} executed")
        with open(f"LA_{date_time}.json", "w", encoding='utf-8') as json_file:
            json.dump(final_content, json_file, indent=4, ensure_ascii=False)


@timer
def mainthread():
    get_author_content()
    save_content_to_json()


if __name__ == '__main__':
    mainthread()
    print("=== Process finished successfully! ===")