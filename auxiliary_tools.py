import json
from datetime import datetime
from parsing_tools_3 import Author
from typing import List, Dict, Set, Tuple, Any, Callable, Generator


def timer(func: Callable) -> Callable:
    def wrap(*args, **kwargs):
        start = datetime.now()
        res = func(*args, **kwargs)
        time = datetime.now() - start
        print(f"[Timer information] Function {func.__name__!r} executed in time: {str(time)[:7]}")
        return res
    return wrap


def show_dict_as_json(dict_: Dict) -> json:
    return json.dumps(dict_, indent=4, ensure_ascii=False)


def create_temp_file(all_authors_list: List) -> None:
    all_authors_for_json = [author.author_obj_into_dict() for author in all_authors_list]
    with open(f"TEMP_all_authors.json", "w", encoding='utf-8') as jf:
        json.dump(all_authors_for_json, jf, indent=4, ensure_ascii=False)


def get_author_content_from_json_file() -> Generator[Tuple[Author, int], None, None]:
    filename = "LA_all_authors_FULL.json"
    with open(filename) as jf:
        all_authors_from_json = json.load(jf)

    # Variable 'all_authors_list' contains all authors collected in 3 languages,
    # and their data except 'events'
    all_authors_list = [Author.author_dict_into_obj(i) for i in all_authors_from_json]

    count_authors = len(all_authors_list)
    print(f"[INFO] {count_authors} author{'s are' if count_authors > 1 else ' is'} got from the file:\n{filename!r}")

    for author in all_authors_list:
        yield author, count_authors
