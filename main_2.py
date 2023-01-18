import sys
import requests.exceptions
from requests_html import HTMLSession
from requests_html import HTML

# url = "kalectar_page.txt"
url = "https://kalektar.org"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "cookie": "_ga=GA1.1.31448554.1672925450; i18n_redirected=en; _ga_43WF48JZQM=GS1.1.1672968523.4.1.1672968700.0.0.0",
    "token": "4750ce86-9998-4ee6-9805-36b1a8aef62e"
    }




try:
    session = HTMLSession()
    res = session.get(url, headers=headers)
    print(res.text)
except requests.exceptions.RequestException as reRE:
    print(reRE)
    sys.exit()
#
# letter_vertical_bar = res.html.find("ul.items-list", first=True).find("li[id^='bl']")
# letter_amount = len(letter_vertical_bar)
# print(f"{letter_amount=}")


# for letter in letter_vertical_bar:
#     letter = letter.find("span", first=True)
#     print(letter.text)

# last_letter = letter_vertical_bar[-1].find("span", first=True).text
# print(f"{last_letter=}", end="\n")


# with open('js_script.js', encoding='utf-8') as file:
#     script_text = file.read()

script_text = """
var puppeteer = require('puppeteer');
var url = 'https://kalektar.org';

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  page.on('console', async msg => {
    const args = msg.args();
    const vals = [];
    for (let i = 0; i < args.length; i++) {
      vals.push(await args[i].jsonValue());
    }
    console.log(vals.join('\t'));
  });
  await page.goto(url);
  await page.evaluate(()=> {
    
    const wait = (duration) => { 
      console.log('waiting', duration);
      return new Promise(resolve => setTimeout(resolve, duration)); 
    };

    (async () => {
      
      window.atBottom = false;
      const scroller = document.documentElement;
      let lastPosition = -1;
      while(!window.atBottom) {
        scroller.scrollTop += 1000;
        await wait(300);
        const currentPosition = scroller.scrollTop;
        if (currentPosition > lastPosition) {
          console.log('currentPosition', currentPosition);
          lastPosition = currentPosition;
        }
        else {
          window.atBottom = true;
        }
      }
      console.log('Done!');

    })();

  });

  await page.waitForFunction('window.atBottom == true', {
    timeout: 900000,
    polling: 1000
  });

  await page.screenshot({path: 'yoursite.png', fullPage: true});

  await browser.close();
})();
"""



res.html.render()
page_1 = res.html.html
print(page_1)

# try:
#     res.html.render(timeout=20, sleep=1, scrolldown=45)
# except requests.exceptions.RequestException as reRE:
#     print("Problems with page scrolling")
#     print(reRE)
# all_letters_block = res.html.find("div.posts-container.scroll-anchor-content", first=True)
# letter_blocks = res.html.find("section.observable-section")
# for letter_block in letter_blocks:
#     letter = letter_block.find("header", first=True)
#     print(f"***{letter.text}***")
#     letter_authors = letter_block.find("div[class*='cell-box cell-box-feed public']")
#     for author in letter_authors:
#         letter_author_name = author.find("span.title", first=True)
#         letter_author_occupation = author.find("div[class*='short-description desc']", first=True)
#         print(f"{letter_author_name.text!r} [{letter_author_occupation.text}]")
#     print()




