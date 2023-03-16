import asyncio
import requests
from bs4 import BeautifulSoup
import json
from db import BotDB
import time


def save_html(url):
  #send request to the website
  headers = {'Accept-Language': 'ru', 'Content-Type': 'text/html; charset=utf-8'}
  r = requests.get(url, headers=headers)

  #fething the page source of the website
  html_content = r.content

  #parse source code of the website
  soup = BeautifulSoup(markup=html_content, features="html.parser")

  return soup


def parse_page(url):
  all_problems = []

  content = save_html(url)
  content = content.find("table", attrs={"class": "problems"})

  for item in content.find_all('tr'):
    f = item.find_all('td')
    if f:
      d = {}
      topic = [i.get_text().strip('\n ') for i in f[1].find_all('a')]
      del topic[0]
      if not topic:
        topic = 'null'
      else:
        topic = f'ARRAY{topic}'
      url = f[0].find('a').get('href')
      number = f[0].get_text().strip(' \t\n\r')
      name = f[1].find('div').get_text().strip(' \t\n\r')
      compexity = f[3].get_text().strip(' \t\n\r')
      if compexity == '':
        compexity = 0
      else:
        compexity = int(compexity)
      solved = f[4].get_text().strip(' \t\n\r')
      if solved != '':
        solved = int(''.join(filter(str.isdigit, solved)))
      else:
        solved = 0

      d["number"] = f"'{number}'"
      d['name'] = f"'{name}'"
      d["topic"] = topic
      d['complexity'] = compexity
      d['solved'] = solved
      d["url"] = f"'{url}'"

      all_problems.append(d)

  return all_problems


def check_url(url):
  try:
    response = requests.get(url)
    if response.status_code == 200:
      print('well')
      return True
    else:
      print('bad')
      return False
  except requests.exceptions.RequestException as e:
    print(e)
    return False



def count_pages(url):
  pages = []
  html = save_html(url)
  html = html.find("div", attrs={"class": "pagination"})
  for item in html.find_all('span'):
    num_page = item.get('pageindex')
    if num_page:
      pages.append(int(num_page))
  return max(pages)



async def parse_all_pages(bot_db):
  url = f'https://codeforces.com/problemset/page/1?order=BY_RATING_ASC'
  num = count_pages(url)
  await bot_db.create_pool()
  for i in range(1, num+1):
    if check_url(url):
      problems = parse_page(url)
      await bot_db.add_problem(problems)
      url = f'https://codeforces.com/problemset/page/{i}?order=BY_RATING_ASC'
  await bot_db.release_pool()


def process_parse():
  bot_db = BotDB()
  while True:
    asyncio.run(parse_all_pages(bot_db))
    time.sleep(3600)



if __name__=="__main__":
  parse_all_pages()
