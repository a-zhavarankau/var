import sys
import pyppeteer.errors
import requests
import fake_useragent
from requests_html import HTMLSession
from datetime import datetime
from parsing_tools import get_authors_by_letter, get_author_events, get_event_data
from copy import deepcopy
from config import P_ST_MSG, URL
import json


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
        print(f"[ERROR] {reRE}{P_ST_MSG}")
        sys.exit()
    if response.status_code == 200:
        return response
    else:
        print("[ERROR] Response is not OK (status code is not 200). Check the URL.{P_ST_MSG}")


def get_response_per_scroll(response):
    """ Take the main response and provide JS script during 'render()' function.
        Script performs 'scrolls' amount per every script execution.
        'js_out' is script's output that contain new coordinate of scrolled page bottom
        and result ("1" - if the main page's bottom is reached, "0" - in other case).
    """
    js_out = {'result': 0}
    counter = -1  # Started from '-1' to load first unscrolled page (usually '0')
    scrolls = 5
    scroll_height = 300
    while js_out['result'] == 0:
        # Here, JavaScript is used to imitate scrolldown at the page.
        # Scrolls' amount per JS iteration = 'step'.
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
                  f"{P_ST_MSG}")
            sys.exit()
        except Exception as exc:
            print(f"[ERROR] {exc}")
        else:
            yield response

def get_author_content():
    """ Prepare the whole content (author's data + events' data) to save. """
    print("[INFO] Process started =>")
    url = URL
    response = get_main_response_and_check_200(url)

    all_authors = []
    gen = get_response_per_scroll(response)
    count_authors = 0
    while True:
        try:
            next_response = next(gen)
            authors_per_scroll = get_authors_by_letter(next_response)
            for author in authors_per_scroll:
                if author not in all_authors:
                    all_authors.append(author)
                    count_authors += 1
        except StopIteration:
            break

    print(all_authors)
    print(f"[INFO] {count_authors} author{'s are' if count_authors > 1 else ' is'} collected from the site.")
    #
    # with open("all_authors_no_letter.json", "w") as jf:
    #     json.dump(all_authors, jf, indent=4, ensure_ascii=True)

    # with open("all_authors_no_letter.json") as jf:
    #     all_authors = json.load(jf)

    count_authors = len(all_authors)
    for author in all_authors:
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
        with open(f"LA_{date_time}.json", "w") as json_file:
            json.dump(final_content, json_file, indent=4)


@timer
def mainthread():
    get_author_content()
    save_content_to_json()


if __name__ == '__main__':
    mainthread()
    print("=== Process finished successfully! ===")