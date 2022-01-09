import hashlib
import json
import os
import requests
import sys

from bs4 import BeautifulSoup
from utils import get_project_root, update_checksum

def main():
  file_path = os.path.join(get_project_root(), 'data', 'category.json')
  file_min_path = os.path.join(get_project_root(), 'data', 'category_min.json')
  url = 'https://hololive.hololivepro.com/talents'
  res = requests.get(url)
  data = []

  Soup = BeautifulSoup(res.text, 'html.parser')
  Soup_res = Soup.find(id='nav_tag').findAll('a')

  for index, item in enumerate(Soup_res):
    data.append({ 'label': item.get_text(), 'url': item.get('href') })

  check_code = hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()

  with open(file_path, 'w', encoding='utf-8') as f:
    json.dump({ 'data': data }, f, indent=2, ensure_ascii=False)
  with open(file_min_path, 'w', encoding='utf-8') as f:
    json.dump({ 'data': data }, f, ensure_ascii=False)

  update_checksum('category', check_code)

if __name__ == '__main__':
  sys.exit(main())
