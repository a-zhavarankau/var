import json
import fake_useragent
from datetime import datetime
from parsing_tools_4 import Author
from typing import List, Dict, Tuple, Callable, Generator


def timer(func: Callable) -> Callable:
    def wrap(*args, **kwargs):
        start = datetime.now()
        res = func(*args, **kwargs)
        time = datetime.now() - start
        print(f"[Timer information] Function {func.__name__!r} executed in time: {str(time)[:7]}")
        return res
    return wrap


def get_headers(fake_user_agent: bool = False) -> Dict[str, str]:
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


def show_dict_as_json(dict_: Dict) -> json:
    return json.dumps(dict_, indent=4, ensure_ascii=False)


def create_temp_file_json(all_authors_list: List,
                          filename: str = "TEMP_all_authors") -> None:
    all_authors_for_json = [author.author_obj_into_dict() for author in all_authors_list]
    with open(f"{filename}.json", "w", encoding='utf-8') as jf:
        json.dump(all_authors_for_json, jf, indent=4, ensure_ascii=False)


def NO_get_author_content_from_json_file(filename) -> Generator[Tuple[Author, int], None, None]:
    with open(filename) as jf:
        all_authors_from_json = json.load(jf)

    # Variable 'all_authors_list' contains all authors collected in 3 languages,
    # and their data except 'events'
    all_authors_list = [Author.author_dict_into_obj(i) for i in all_authors_from_json]

    count_authors = len(all_authors_list)
    print(f"[INFO] {count_authors} author{'s are' if count_authors > 1 else ' is'} got from the file:\n{filename!r}")

    for author in all_authors_list:
        yield author, count_authors
