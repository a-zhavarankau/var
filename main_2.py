import sys
import pyppeteer.errors
import requests
import fake_useragent
from requests_html import HTMLSession
from parsing_tools import get_letters_and_authors, get_author_events
from config import P_ST_MSG


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


def get_content():
    print("[INFO] Process started =>")
    url = "https://kalektar.org"
    response = get_main_response_and_check_200(url)

    base = {}

    """Here, we get letters+authors one-by-one.
       We can add them to the dict, list, DB, etc."""

    file = open("LA.txt", "a", encoding='utf-8')

    letters_and_authors = get_letters_and_authors(response)
    for item in letters_and_authors:
    #     print(letters_and_authors)
    # gen = get_letters_and_authors(response)
    # while True:
    #     try:
    #         letters_and_authors = next(gen)
    #     except StopIteration:
    #         break
        letter = (lambda a: [k for k, _ in a.items()])(item)[0]
        print(f"*** {letter} ***")
        # print(item, "\n")
        # file.write(f"{item}\n")

        headers = get_headers(fake_user_agent=True)
        author_data = (lambda a: [v for _, v in a.items()])(item[letter])[0]
        author_link = author_data['link']
        author_events = get_author_events(author_link, headers)
        author_data['events'] = []
        for event in author_events:
            author_data['events'].append(event)
        print(f"{item=}")

    file.close()
    # for letter in letters:
    #     authors = get_authors_by_letter(response, letter)
    # for author in authors:
    #     get_events_by_author(author_link)



def save_content_to_():
    pass



def mainthread():
    get_content()
    save_content_to_()


if __name__ == '__main__':
    mainthread()