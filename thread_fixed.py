import json
from parsing_tools_4 import Author


# with open("TEMP_en_authors.json") as jf_be:
#     list_en = json.load(jf_be)
#     list_en = [Author.author_dict_into_obj(i) for i in list_en]
#
# with open("TEMP_be_authors.json") as jf_be:
#     list_be = json.load(jf_be)
#     list_be = [Author.author_dict_into_obj(i) for i in list_be]
#
# with open("TEMP_ru_authors.json") as jf_be:
#     list_ru = json.load(jf_be)
#     list_ru = [Author.author_dict_into_obj(i) for i in list_ru]
#
# all_authors_dict = {'en': list_en, 'be': list_be, 'ru': list_ru}
# for i in all_authors_dict.items():
#     print(i)


with open("MAsync_2023.04.23__18:57.json") as first, open("MAsync_2023.05.13__01:21.json") as second:
    list_1 = json.load(first)
    list_2 = json.load(second)
    list_f = [Author.author_dict_into_obj(i) for i in list_1]
    list_s = [Author.author_dict_into_obj(i) for i in list_2]


print(len(list_f))
print(len(list_s))

print("New authors")
for s in list_s:
    if s not in list_f:
        print(s)

print("\nOld authors")
for f in list_f:
    if f not in list_s:
        print(f)
