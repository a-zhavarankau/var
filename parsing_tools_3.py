import sys
import requests.exceptions
import requests_html
from itertools import product
import time
from typing import List, Dict, Set, Tuple, Any
from config import PROC_STOP_MSG, NA_SIGN, URL


class Author:
    def __init__(self, link, name_en=None, name_be=None, name_ru=None,
                 occupation=None, source=None, events=None):
        self.link = link
        self.name_en = name_en
        self.name_be = name_be
        self.name_ru = name_ru
        self.occupation = occupation
        self.source = source or URL
        self.events = events or []

    def author_obj_into_dict(self):
        key_order = ('name_en', 'name_be', 'name_ru', 'occupation', 'link', 'source', 'events')
        author_dict = dict((k, self.__dict__[k]) for k in key_order)
        return author_dict

    def __str__(self):
        return str(self.author_obj_into_dict())

    def __eq__(self, other):
        return self.link == other.link

    @staticmethod
    def author_dict_into_obj(author_dict):
        author = Author(**author_dict)
        return author


def get_letter_block(response):
    letter_blocks = response.html.find("section.observable-section")
    for letter_block in letter_blocks:
        yield letter_block


def get_authors_by_letter(response, lang) -> Author:
    ##################### get_author_by_letter
    """ Yield an object of class Author (that contains all data except 'events')
        from the letter block.
    """
    for letter_block in get_letter_block(response):
        authors_in_letter = letter_block.find("div[class*='cell-box cell-box-feed public']")
        for author_block in authors_in_letter:
            author_name = author_block.find("span.title", first=True).text
            author_occupation = author_block.find("div[class*='short-description desc']", first=True).text
            author_token = author_block.find("a.post-link-box", first=True).links
            author_link = f"https://kalektar.org{author_token.pop()}"

            # Make all 'author_link' without "be" and "ru" attachments
            author_link = author_link.replace("/ru", "") if "/ru" in author_link else author_link.replace("/be", "")
            author = Author(link=author_link, occupation=author_occupation)
            author.__dict__[f"name_{lang}"] = author_name
            yield author


def get_author_events(author_link, headers) -> Tuple[List, Any]:
    """ Return list of author events + session
    """
    session_2 = requests_html.HTMLSession()
    for i in range(10):
        try:
            response_2 = session_2.get(url=author_link, headers=headers) # <<<<< requests.exceptions.ConnectTimeout: HTTPSConnectionPool(host='kalektar.org', port=443): Max retries exceeded with url: /names/uIjr1NOmQZ7hs7hRCg8a (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x10a485360>, 'Connection to kalektar.org timed out. (connect timeout=None)'))
        except requests.exceptions.ConnectTimeout:
            if i < 9:
                print(f"[ERROR] Connection issue. Attempt to reconnect #{i+1} of 10 after 30 seconds...")
                time.sleep(30)
                continue
            print(f"Connection can not be established.{PROC_STOP_MSG}")
            sys.exit()
        else:
            page_2 = requests_html.HTML(html=response_2.text)
            events = page_2.find("div[class*='cell-box cell-box-ref public event']")
            return events, session_2

def get_event_data(event, session_2, headers):
    event_token = event.find("a.post-link-box")[0].links
    event_link = "https://kalektar.org" + event_token.pop()

    response_3 = session_2.get(url=event_link, headers=headers)
    page_3 = requests_html.HTML(html=response_3.text)
    try:
        event_name = page_3.find("h1[class*='post-title translation-view']", first=True).text
    except AttributeError:
        event_name = NA_SIGN

    try:
        event_dates_block = page_3.find("span[class*='dates-string inline-block']")
        event_dates = "".join([date.text for date in event_dates_block])
    except AttributeError:
        event_dates = NA_SIGN

    try:
        event_place = page_3.find("div.translation-editor-view", first=True).text
    except AttributeError:
        try:
            event_place = page_3.find("div.translation-auto-view", first=True).text
        except AttributeError:
            try:
                event_place = page_3.find("div.translation-undefined-view", first=True).text
            except AttributeError:
                event_place = NA_SIGN

    event_name_dict = {'event_name': event_name}
    event_dates_dict = {'event_dates': event_dates}
    event_place = event_place.replace("\xa0\xa0\xa0", ";")
    event_place_dict = {'event_place': event_place}
    event_link_dict = {'event_link': event_link}
    event_dict = event_name_dict | event_dates_dict | event_place_dict | event_link_dict
    return event_dict
