import hashlib
import json
import os
import requests
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import Dict
from utils import get_project_root, update_checksum

def main():
  file_path = os.path.join(get_project_root(), 'data', 'member_detail.json')
  file_min_path = os.path.join(get_project_root(), 'data', 'member_detail_min.json')
  member_url = 'https://raw.githubusercontent.com/wooxer88/Crawler-Hololive/main/data/member_min.json'
  member_res = requests.get(member_url)
  member_json = json.loads(member_res.text)['data']
  detail_data = {}

  for item in member_json['ALL']:
    detail_data[item['name']] = member_detail(item['url'])

  check_code = hashlib.sha256(json.dumps(detail_data).encode('utf-8')).hexdigest()

  with open(file_path, 'w', encoding='utf-8') as f:
    json.dump({ 'data': detail_data }, f, indent=2, ensure_ascii=False)
  with open(file_min_path, 'w', encoding='utf-8') as f:
    json.dump({ 'data': detail_data }, f, ensure_ascii=False)

  update_checksum('member_detail', check_code)

def member_avatar(type, url):
  driver_path = os.path.join(get_project_root(), 'webdriver', 'chromedriver.exe')
  options = Options()
  options.add_argument('headless')
  options.add_argument('--disable-notifications')
  ser = Service(driver_path)

  driver = webdriver.Chrome(options=options, service=ser)

  def avatar_twitter(url):
    driver.get(url + '/photo')

    try:
      element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="圖片"]'))
      )

      Soup = BeautifulSoup(driver.page_source, 'html.parser')
      Soup_res = Soup.find('img', alt="圖片", src=True)

      return Soup_res.get('src')
    finally:
      driver.quit()

  def avatar_youtube(url):
    driver.get(url)

    try:
      selector = '#channel-header-container #img'
      element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
      )

      Soup = BeautifulSoup(driver.page_source, 'html.parser')
      Soup_res = Soup.select_one(selector)

      return Soup_res.get('src')
    finally:
      driver.quit()

  if type == 'twitter':
    return avatar_twitter(url)
  if type == 'youtube':
    return avatar_youtube(url)

def member_detail(url) -> Dict:
  res = requests.get(url)
  data = {}

  Soup = BeautifulSoup(res.text, 'html.parser')
  Soup_res = Soup.find(class_='talent_top')

  figure = []

  about = Soup_res.find(class_='txt').text
  slogan = Soup_res.find(class_='catch').text
  url_twitter = Soup_res.find(class_='t_sns').find('a', string='Twitter').get('href')
  url_youtube = Soup_res.find(class_='t_sns').find('a', string='YouTube').get('href').split('?')[0]

  for item in Soup_res.find(id='talent_figure').find('figure').find_all('img'):
    figure.append(item.get('src'))

  data['avatar'] = {}
  data['about'] = about
  data['slogan'] = slogan
  data['url'] = { 'twitter': url_twitter, 'youtube': url_youtube }

  for key, value in data['url'].items():
    data['avatar'][key] = member_avatar(key, value)

  return data

if __name__ == '__main__':
  sys.exit(main())
