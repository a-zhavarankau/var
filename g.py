import requests_html
import json
from main_2 import change_order_in_author_data

# with open("LA_06.02.2023_all_authors_dict_en.json") as fen, open("LA_06.02.2023_all_authors_dict_be.json") as fbe, open("LA_06.02.2023_all_authors_dict_ru.json") as fru, open("LA_06.02.2023_all.json") as fa:
#     fen = json.load(fen)
#     fbe = json.load(fbe)
#     fru = json.load(fru)
#     fa = json.load(fa)
#
#     print(f"{len(fen)=}, {len(fbe)=}, {len(fru)=}")
#     sfen = set(fen)
#     sfbe = set(fbe)
#     sfru = set(fru)
#
#     print(f"{len(sfen - sfbe) =}")
#     print(f"Links in 'fen' but not in 'fbe': {sfen - sfbe}")
#     print(f"{len(sfbe - sfen) =}")
#     print(f"Links in 'fbe' but not in 'fen': {sfbe - sfen}")
#     print(f"{len(sfen - sfru) =}")
#     print(f"Links in 'fen' but not in 'fru': {sfen - sfru}")
#     print(f"{len(sfru - sfen) =}")
#     print(f"Links in 'fru' but not in 'fen': {sfru - sfen}")
#
#     print(f"{len(fa) =}")


"""Author not in dict: https://kalektar.org/names/WBgx6smtZl4HwNOnQAjx (Михаил (Моисей) Векслер)
Scrolling 3: {'result': 0, 'coordinates': 4200}
Author not in dict: https://kalektar.org/names/1zXLXBz8dsYBgRLipu9t (КХ (пространство))
Author not in dict: https://kalektar.org/names/oWmUSZJgE1Ym1bUt8ccb (Шестая линия)
Scrolling 4: {'result': 0, 'coordinates': 5700}
Author not in dict: https://kalektar.org/names/Jj5RqflMPiz51neoIUib (DOTYK)
Author not in dict: https://kalektar.org/names/D7FxoOIO767tYKKJVpdy (KALEKTAR)
Author not in dict: https://kalektar.org/names/hE6eofAiGugcNHgGmVxO (NOVA)"""

author3 = {"https://kalektar.org/names/hE6eofAiGugcNHgGmVxO": {"name_en": "NOVA", "name_be": "N/A", "name_ru": "NOVA", "occupation": "gallery", "link": "https://kalektar.org/names/hE6eofAiGugcNHgGmVxO", "source": ["https://kalektar.org"]}}

author4 = {"https://kalektar.org/names/oWmUSZJgE1Ym1bUt8ccb": {"name_en": "Шестая линия", "occupation": "галерея", "link": "https://kalektar.org/names/oWmUSZJgE1Ym1bUt8ccb", "source": ["https://kalektar.org"]}}

authors = {"https://kalektar.org/names/hE6eofAiGugcNHgGmVxO": {"name_en": "NOVA", "name_be": "N/A", "name_ru": "NOVA", "occupation": "gallery", "link": "https://kalektar.org/names/hE6eofAiGugcNHgGmVxO", "source": ["https://kalektar.org"]},
           "https://kalektar.org/names/oWmUSZJgE1Ym1bUt8ccb": {"name_en": "Шестая линия", "occupation": "галерея", "link": "https://kalektar.org/names/oWmUSZJgE1Ym1bUt8ccb", "source": ["https://kalektar.org"]},
    'https://kalektar.org/names/xBPefZZQhf27YgEUZoEH': {'name_en': 'Leonid Shchemelev\nautomatic translation', 'name_be': 'Леанід Шчамялёў\nаўтаматычны пераклад', 'name_ru': 'Леонид Щемелёв', 'occupation': 'artist', 'link': 'https://kalektar.org/names/xBPefZZQhf27YgEUZoEH', 'source': ['https://kalektar.org']},
           "https://kalektar.org/names/WBgx6smtZl4HwNOnQAjx": {"name_en": "Michael Veksler", "name_be": "N/A", "name_ru": "Михаил (Моисей) Векслер", "occupation": "artist, illustrator", "link": "https://kalektar.org/names/WBgx6smtZl4HwNOnQAjx", "source": ["https://kalektar.org"]},
     "https://kalektar.org/names/IbF8IVYrvVtcqRI3dALu": { "name_en": "Tasha Arlova", "occupation": "artist, curator, film director", "link": "https://kalektar.org/names/IbF8IVYrvVtcqRI3dALu", "source": ["https://kalektar.org"], "name_be": "Таша Арлова"}}

authors2 = {"https://kalektar.org/names/WBgx6smtZl4HwNOnQAjx": {"name_en": "Michael Veksler", "occupation": "artist, illustrator", "link": "https://kalektar.org/names/WBgx6smtZl4HwNOnQAjx", "source": ["https://kalektar.org"]}}

langs = {"en": "", "be": "/be", "ru": "/ru"}


for author in authors:
    author_data = authors[author]
    for lang in langs:
        # if not author_data.get("name_" + lang):
        #     continue
        if not author_data.get("name_" + lang) or author_data["name_" + lang] == "N/A":
            print(author_data["name_en"], f"has N/A name field in langeage \'{lang}\'")
            print(author_data.get("name_" + lang, "empty"), "-> ", end="")
#         for lang in langs:
            link = author_data["link"][:-27] + langs[lang] + author_data["link"][-27:]
            session = requests_html.HTMLSession()
            resp = session.get(link)
            if resp.status_code != 200:
                continue
            try:
                name = resp.html.find("h1.post-title", first=True).text
                if "\n" in name:
                    name = name.replace("\n", " (") + ")"
                # if name == "N/A":
                #     break
            except AttributeError:
                name = "N_A"
            print(name)
#             author_data["name_" + lang] = name
#         break
#     author_data_new = change_order_in_author_data(author_data)
#     authors[author] = author_data_new
#
# for k, v in authors.items():
#     print(f"{k}: {v}")




# for author in authors:
#     author_data = authors[author]
#     for lang in langs:
#         if author_data.get("name_" + lang) and not author_data["name_" + lang] == "N/A":
#             continue
#         print(author_data.get("name_" + lang, "empty"), "-> ", end="")
#         for lang in langs:
#             link = author_data["link"][:-27] + langs[lang] + author_data["link"][-27:]
#             session = requests_html.HTMLSession()
#             resp = session.get(link)
#             if resp.status_code != 200:
#                 continue
#             try:
#                 name = resp.html.find("h1.post-title", first=True).text
#                 if "\n" in name:
#                     name = name.replace("\n", " (") + ")"
#                 # if name == "N/A":
#                 #     break
#             except AttributeError:
#                 name = "N_A"
#             print(name)
#             author_data["name_" + lang] = name
#         break
#     author_data_new = change_order_in_author_data(author_data)
#     authors[author] = author_data_new
#
# for k, v in authors.items():
#     print(f"{k}: {v}")

# name = "Заслужаны дзеяч мастацтваў Беларусі (узнагарода)\nаўтаматычны пераклад"
# # name = name.replace("\nautomatic translation", " (automatic translation)")
# if "\n" in name:
#     name = name.replace("\n", " (") + ")"
#
# print(name)


# nova_vol = author3[tuple(author3)[0]]
# for lang in langs:
#     if nova_vol["name_"+lang] == "N/A":
#         link = nova_vol["link"][:-27] + langs[lang] + nova_vol["link"][-27:]
#         session = requests_html.HTMLSession()
#         resp = session.get(link)
#
#         name = resp.html.find("h1.post-title", first=True).text
#         print(name)
#         nova_vol["name_"+lang] = name


        # print(author_name)




# author1 = {'https://kalektar.org/names/rsELkYVQthnOVE4ZpGJs': {'name_en': '#дамаудобнаявбыту ("дама зручная ў побыце")', 'occupation': 'група', 'link': 'https://kalektar.org/names/rsELkYVQthnOVE4ZpGJs', 'source': ['https://kalektar.org']}}
# author2 = {'https://kalektar.org/names/xL2QTq7r4uulIT0r7LfK': {'name_en': '1+1=1', 'occupation': 'duet', 'link': 'https://kalektar.org/names/xL2QTq7r4uulIT0r7LfK', 'source': ['https://kalektar.org']}}
#
#
# author_data = [v for _, v in author1.items()][0]
# author_add_name = author_data['name_en']
# print("link" in author_data)
#
# with open("LALALA.json", "a") as jf:
#     json.dump(author1, jf, indent=4, ensure_ascii=False)
#     json.dump(',', jf, indent=4, ensure_ascii=False)
#
# with open("LALALA.json", "a") as jf:
#     json.dump(author2, jf, indent=4, ensure_ascii=False)

# author_from_dict = {'name_en': '#дамаудобнаявбыту ("lady comfortable at home")', 'occupation': 'group',
#  'link': 'https://kalektar.org/names/rsELkYVQthnOVE4ZpGJs', 'source': ['https://kalektar.org'],
#  'name_be': '#дамаудобнаявбыту ("дама зручная ў побыце")', 'name_ru': '#дамаудобнаявбыту'}




