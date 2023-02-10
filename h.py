# link = "huirefniuer"
# author_fields = ("name_en", "name_be", "name_ru", "occupation", "link", "source")
# dict_author_data = dict.fromkeys(author_fields)
# # dict_author_data = {link: dict_author_data_value}
# print(dict_author_data)
# if not dict_author_data.get("name_en"):
#     dict_author_data["name_en"] = "angl_name"
#
# print(dict_author_data)
import requests_html

from config import *
import json
from parsing_tools_3 import Author, get_authors_by_letter
from main_3 import author_dict_into_obj, get_headers
from datetime import datetime

data = datetime.now().strftime("%d.%m.%Y")

author1 = Author(link="https://kalektar.org/names/u7epW6hT06n2awXY4ddu", name_en='Abram Veksler', occupation='artist')
# print(author1)
# print(author1.name_be)
lang = "ru"
nn = f"name_{lang}"
# print(nn)
# for lang in ("en", "be", "ru"):
    # print(author1.__dict__[f"name_{lang}"])

author_d = {'name_en': 'Anatoly Anikeichik', 'name_be': None, 'name_ru': None, 'occupation': 'artist, teacher', 'link': 'https://kalektar.org/names/ZU6gKeHY3Ga6arZ1yCdH', 'source': 'https://kalektar.org', 'events': None}

def author_obj_into_dict(author):
    key_order = ('name_en', 'name_be', 'name_ru', 'occupation', 'link', 'source', 'events')
    author_dict = dict((k, author.__dict__[k]) for k in key_order)
    return author_dict

# def author_obj_into_json(author):
#     author_dict = author_obj_into_dict(author)
#     return json.dumps(author_dict, indent=4, ensure_ascii=False)

# print(author_obj_into_dict(author1))
# author_json = author_obj_into_json(author1)
# print(author_json)


def author_dict_to_obj(author_dict):
    author = Author(**author_dict)
    return author

# def author_json_into_obj(author_json):
#     author_dict = json.loads(author_json)
#     author = Author(**author_dict)
#     return author

# print(author_dict_to_obj(author_d))
# author_1_obj = author_json_into_obj(author_json)
# print(author_1_obj)


author2 = Author(link="https://kalektar.org/names/123454321", name_en='Andrei', occupation='artist')
# print(type(author2.author_obj_into_dict()), author2.author_obj_into_dict())
# print(type(author2), author2)

author3 = Author(link="https://kalektar.org/names/asddgfdsa", name_en='Victor', occupation='gallerist')
author4 = Author(link="https://kalektar.org/names/a1s2d3f4g5", name_en='Ivan', occupation='musician')
author5 = Author(link="https://kalektar.org/names/asddgfdsa", name_be='Вiктар', occupation='gallerist')

# print(author3 == author5)
authors = []
for i in (author2, author3, author4, author5):
    if i not in authors:
        authors.append(i)

# for i in authors: print(i)





authors_for_json = [author_obj_into_dict(i) for i in authors]
# print(authors_for_json)
filename = "LA_authors_primer.json"

# with open(filename, "w", encoding='utf-8') as jf:
#     json.dump(authors_for_json, jf, indent=4, ensure_ascii=False)
#
# author4_for_json = author_obj_into_dict(author4)
#
# with open(filename, "w", encoding='utf-8') as jf:
#     authors_for_json.append(author4_for_json)
#     json.dump(authors_for_json, jf, indent=4, ensure_ascii=False)

def show_dict_as_json(file):
    with open(file) as jf:
        json_data = json.load(jf)
    return json.dumps(json_data, indent=4, ensure_ascii=False)

output = show_dict_as_json(filename)
# print(output)




# with open(f"LA_{data}_authors_without_all_names.json") as jf:
#     authors_without_all_names_json = json.load(jf)
#     authors_without_all_names = [author_dict_into_obj(i) for i in authors_without_all_names_json]
#
# print(len(authors_without_all_names))
#
# headers = get_headers(fake_user_agent=True)
# session = requests_html.HTMLSession()
# langs = {"en": "", "be": "/be", "ru": "/ru"}
# count = 0
# for author in authors_without_all_names:
#     for lang in ("en", "be", "ru"):
#         if author.__dict__[f"name_{lang}"] is None:
#             author_link = author.link.replace("/names", f"{langs[lang]}/names")
#             print(author_link)
#             resp = session.get(url=author_link, headers=headers)
#             try:
#                 author_name = resp.html.find("h1[class*='post-title translation-view']", first=True).text
#             except AttributeError:
#                 author_name = f"{NA_SIGN} ({author.name_en})"
#             author.__dict__[f"name_{lang}"] = author_name
#             print(f"name_{lang} = ", author.__dict__[f"name_{lang}"])
#     count += 1
#     print(count, author)
#
#
# authors_without_all_names_json = [i.author_obj_into_dict() for i in authors_without_all_names]
# with open(f"LA_{data}_authors_without_all_names_fixed.json", "w", encoding='utf-8') as jf:
#     json.dump(authors_without_all_names_json, jf, indent=4, ensure_ascii=False)


with open(f"LA_10.02.2023_all_authors_unchecked.json") as jf:
        all_authors = json.load(jf)
        all_authors_unchecked = [author_dict_into_obj(i) for i in all_authors]
print(len(all_authors_unchecked))










"""
def author_obj_into_dict(author):
    key_order = ('name_en', 'name_be', 'name_ru', 'occupation', 'link', 'source', 'events')
    author_data = dict((k, author.__dict__[k]) for k in key_order)
    author_dict = {author.link: author_data}
    return author_dict

def author_obj_into_json(author):
    author_dict = author_obj_into_dict(author)
    return json.dumps(author_dict, indent=4, ensure_ascii=False)

# print(author_obj_into_dict(author1))
author_json = author_obj_into_json(author1)
# print(author_json)

def author_dict_to_inst(author_dict):
    author_data = tuple(v for _, v in author_dict.items())[0]
    author = Author(**author_data)
    return author

def author_json_into_obj(author_json):
    author_dict = json.loads(author_json)
    author_data = tuple(v for _, v in author_dict.items())[0]
    author = Author(**author_data)
    return author

# print(author_dict_to_inst(author_d))
author_1_obj = author_json_into_obj(author_json)
# print(author_1_obj.name_en)
"""



""" For JSON:

import json
dict_ = {"User" :{"Name" : "SQWiperYT", "ID" : 10, "Other" : {"ID" : 1}}}


class OurObject:
    def __init__(self, /, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
      
      
x = json.dumps(dict_)
y = json.loads(x, object_hook=lambda d: OurObject(**d))

# See How it Works
y.User
>>> OurObject(ID=10, Name='SQWiperYT', Other=OurObject(ID=1))
y.User.ID
>>> 10
y.User.Name
>>> 'SQWiperYT'
y.User.Other.ID
>>> 1
"""