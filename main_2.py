import sys
import pyppeteer.errors
import requests
import fake_useragent
from requests_html import HTMLSession
from datetime import datetime
from parsing_tools import get_letters_and_authors, get_author_events, get_event_data
from copy import deepcopy
from config import P_ST_MSG
import json


def timer(func):
    def wrap(*args, **kwargs):
        start = datetime.now()
        res = func(*args, **kwargs)
        time = datetime.now() - start
        print(f"Function {func.__name__!r} executed in time: {time}")
        return res
    return wrap


def get_headers(fake_user_agent=False):
    """ Returns headers containing fake useragent if agrument 'fake_user_agent'=True (default=False),
        else original useragent """

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
    js_out = {'result': 0}
    counter = -1  # Started from '-1' to load first unscrolled page (usually '0')
    scrolls = 5
    scroll_height = 300
    while js_out['result'] == 0:
        # Here, JavaScript is used to imitate scrolldown at the page.
        # Scrolls' amount per JS iteration = 'step'.
        scr_down55 = f'(function down() {{let y={counter}; for(let i={scrolls}*y;i<{scrolls}*(y+1);i++) ' \
                     f'{{if ((window.scrollY + window.innerHeight) >= document.body.scrollHeight) {{' \
                     f'return {{result: 1, coordinates: window.pageYOffset}}; }};' \
                     f'window.scrollTo(0, i*{scroll_height});' \
                     f'}};' \
                     f'return {{result: 0, coordinates: window.pageYOffset}}' \
                     f'}})()'
        counter += 1
        try:
            js_out = response.html.render(timeout=30, sleep=2, script=scr_down55)
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
    print("[INFO] Process started =>")
    url = "https://kalektar.org"
    response = get_main_response_and_check_200(url)

    all_authors = []
    # gen = get_response_per_scroll(response)
    # while True:
    #     try:
    #         next_response = next(gen)
    #         authors_per_scroll = get_letters_and_authors(next_response)
    #         # print(list(authors_per_scroll))
    #         for author in authors_per_scroll:
    #             if author not in all_authors:
    #                 author_copy = deepcopy(author)
    #                 all_authors.append(author_copy)
    #     except StopIteration:
    #         break

    # print(all_authors)
    # with open("all_authors.txt", "w") as f:
    #     for author in all_authors:
    #         f.write(f"{author}\n")



    with open("all_authors.txt") as f:
        for item in f:
            yield item
            all_authors.append(item.strip("\n"))

    for author in all_authors:
    #     print(letters_and_authors)
    # gen = get_letters_and_authors(response)
    # while True:
    #     try:
    #         letters_and_authors = next(gen)
    #     except StopIteration:
    #         break
        author = json.load(author)
        print(author)
        letter = (lambda a: [k for k, _ in a.items()])(author)[0]
        author_data = (lambda a: [v for _, v in a.items()])(author[letter])[0]
        author_name = author_data['name']

        headers = get_headers(fake_user_agent=True)
        author_events, session_2 = get_author_events(author_data, headers)
        author_data['events'] = []
        for event in author_events:
            event_data = get_event_data(event, session_2, headers)
            author_data['events'].append(event_data)
            # print(author)
        yield author, author_name


def save_content_to_():
    date_time = datetime.now().strftime("%d-%m-%Y_%H-%M")
    with open(f"LA_{date_time}.txt", "w", encoding='utf-8') as file:
        gen = get_author_content()
        count = 0
        while True:
            try:
                # author_content, author_name = next(gen)
                author_content = next(gen)
            except StopIteration:
                break
            count += 1
            # print(f"[INFO] Author {author_name} executed")
            # print(f"[INFO] Author {count} executed")
            # file.write(f"{author_content}\n")
    print("[INFO] Process successfully finished!")


def mainthread():
    get_author_content()
    save_content_to_()


if __name__ == '__main__':
    mainthread()