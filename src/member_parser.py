import hashlib
import json
import os
import re
import requests
import sys

from bs4 import BeautifulSoup
from typing import List
from utils import get_project_root, update_checksum

en_label_data = ['ホロライブEnglish', 'Myth', 'Project: HOPE', 'Council']
id_label_data = ['ホロライブインドネシア']

def main():
  category_url = 'https://raw.githubusercontent.com/wooxer88/Crawler-Hololive/main/data/category_min.json'
  detail_url = 'https://raw.githubusercontent.com/wooxer88/Crawler-Hololive/main/data/member_detail_min.json'
  category_res = requests.get(category_url)
  category_json = json.loads(category_res.text)['data']
  detail_res = requests.get(detail_url)
  detail_json = json.loads(detail_res.text)['data']
  file_path = os.path.join(get_project_root(), 'data', 'member.json')
  file_min_path = os.path.join(get_project_root(), 'data', 'member_min.json')
  member_data = {}
  overseas_data = {}

  for item in category_json:
    member_data[item['label']] = category_member(item['label'], item['url'])

    if item['label'] in en_label_data or item['label'] in id_label_data:
      for item2 in member_data[item['label']]:
        overseas_data[item2['jp_name']] = item2['name']
  # fix member en and id name in ALL of category
  for item in member_data['ALL']:
    if item['name'] in overseas_data:
      item['name'] = overseas_data[item['name']]

  for item in member_data:
    for item2 in member_data[item]:
      if item2['name'] in detail_json:
        url = item2['url']
        detail = detail_json[item2['name']]

        for item3 in detail: item2[item3] = detail[item3]

        item2['avatar']['hololive'] = item2['img']
        item2['url']['hololive'] = url

        del item2['img']

  check_code = hashlib.sha256(json.dumps(member_data).encode('utf-8')).hexdigest()

  with open(file_path, 'w', encoding='utf-8') as f:
    json.dump({ 'data': member_data }, f, indent=2, ensure_ascii=False)
  with open(file_min_path, 'w', encoding='utf-8') as f:
    json.dump({ 'data': member_data }, f, ensure_ascii=False)

  update_checksum('member', check_code)

def category_member(category, url) -> List:
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

      if name == 'AZKi':
        jp_name = ''
        roman_name = name

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
