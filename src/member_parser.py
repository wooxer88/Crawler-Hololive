import hashlib
import json
import os
import re
import requests
import sys

from bs4 import BeautifulSoup
from typing import List
from utils import get_project_root, update_checksum

def main():
  category_url = 'https://raw.githubusercontent.com/wooxer88/Crawler-Hololive/ae639c1e119eb7052fdfb6d44b84b04e1dc4c9b9/data/category.json'
  category_res = requests.get(category_url)
  category_json = json.loads(category_res.text)['data']
  file_path = os.path.join(get_project_root(), 'data', 'member.json')
  file_min_path = os.path.join(get_project_root(), 'data', 'member_min.json')
  member_data = {}

  for item in category_json:
    member_data[item['label']] = category_member(item['label'], item['url'])

  check_code = hashlib.sha256(json.dumps(member_data).encode('utf-8')).hexdigest()

  with open(file_path, 'w', encoding='utf-8') as f:
    json.dump({ 'data': member_data }, f, indent=2, ensure_ascii=False)
  with open(file_min_path, 'w', encoding='utf-8') as f:
    json.dump({ 'data': member_data }, f, ensure_ascii=False)

  update_checksum('member', check_code)

def category_member(category, url) -> List:
  en_label_data = ['ホロライブEnglish', 'Myth', 'Project: HOPE', 'Council']
  id_label_data = ['ホロライブインドネシア']
  res = requests.get(url)
  data = []

  Soup = BeautifulSoup(res.text, 'html.parser')
  Soup_res = Soup.find(class_='in_talent').find(class_='talent_list').findAll('a')

  for item in Soup_res:
    jp_name = re.sub('\\r|\\n|【卒業生】', '', item.find('h3').contents[0])
    roman_name = item.find('h3').span.text

    if category in en_label_data:
      name = roman_name
    elif category in id_label_data:
      name = roman_name
    else:
      name = jp_name

    data.append({
      'img': item.find('img').get('src'),
      'jp_name': jp_name,
      'name': name,
      'roman': roman_name,
      'url': item.get('href')
    })

  return data

if __name__ == '__main__':
  sys.exit(main())