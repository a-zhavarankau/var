# """
import requests

url0 = "https://kalektar.org"
session = requests.Session()
resp = session.get(url0)
# for i, j in resp.headers.items():
#     print(f"{i}: {j}")
# print(0)

# url1 = "https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel?database=projects/kalektar-org/databases/(default)&VER=8&RID=78870&CVER=22&X-HTTP-Session-Id=gsessionid&$httpHeaders=X-Goog-Api-Client:gl-js/ fire/8.10.1 Content-Type:text/plain X-Firebase-GMPID:1:159379843908:web:675312e312aba743950511 &zx=ftekyt8y4n49&t=1"
url1 = "https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel?database=projects/kalektar-org/databases/(default)&VER=8&RID=78870&CVER=22&X-HTTP-Session-Id=gsessionid"

headers1 = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection": "keep-alive",
    "Content-Length": "609",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "firestore.googleapis.com",
    "Origin": "https://kalektar.org",
    "Referer": "https://kalektar.org/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0",
}
# session1 = requests.Session()
resp1 = session.post(url1)
gsessionid = resp1.headers['X-HTTP-Session-Id']
print(f"{gsessionid=}")
SID = resp1.text.split("\"")[3]
print(f"{SID=}")
print()

url2 = "https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel?database=projects/kalektar-org/databases/(default)&VER=8&RID=86172"
res2 = requests.post(url2)
SID = res2.text.split("\"")[3]
print(f"{SID=}")
# url2_ = "https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel?database=projects/kalektar-org/databases/(default)&VER=8&RID=86172"
# res2 = requests.post(url2_)
# SID_2 = res2.text.split("\"")[3]
# print(f"{SID_2=}")

# url = f"https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel?database=projects/kalektar-org/databases/(default)&gsessionid=DyYXT00LPHvzdVd7nb34uq1h8QUmZezd8eCLC906Gdw&VER=8&RID=rpc&SID=Ax-9TNOMbJqd8u_IjfMa0g&CI=0&AID=0&TYPE=xmlhttp&zx=84b3uf6bqvw0&t=1"
url3 = f"https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel?database=projects/kalektar-org/databases/(default)&gsessionid={gsessionid}&VER=8&RID=rpc&SID={SID}&CI=0&AID=0&TYPE=xmlhttp&zx=84b3uf6bqvw0&t=1"

headers3 = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection": "keep-alive",
    "Host": "firestore.googleapis.com",
    "Origin": "https://kalektar.org",
    "Referer": "https://kalektar.org/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0",
}

resp3 = session.get(url3, headers=headers3)
print(3)
print(resp3)

# "Etag", "Function-Execution-Id", "X-Cloud-Trace-Context", "X-Served-By", "X-Timer"

"""

import requests

url = "https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel?database=projects/kalektar-org/databases/(default)&VER=8&RID=86172"
res = requests.post(url)
SID = res.text.split("\"")[3]
print(SID)

"""