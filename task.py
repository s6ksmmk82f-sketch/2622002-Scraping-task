import time
import csv
import requests
from bs4 import BeautifulSoup
from bs4.exceptions import ParserRejectedMarkup
from urllib.parse import urljoin, urlparse, urldefrag

url = 'https://www.musashino-u.ac.jp'
domain = urlparse(url).netloc

url_list = [url]
visited_url_set = set()
site_map = {}

#for文などで特定のWebサイトに連続アクセスする場合は、必ず time.sleep(秒数) 処理をいれて、負荷をかけないようにする。
for _ in range(10):
    time.sleep(1)
    print("hogehoge")

max_pages = 1000

while url_list:
    current_url = url_list.pop(0)
    current_url = urldefrag(current_url)[0]
    
    if len(visited_url_set) >= max_pages:
        break

    if current_url in visited_url_set:
        continue

    visited_url_set.add(current_url)

    #アクセス前に待って、Webサイトへの負荷を抑える
    time.sleep(1)

    try:
        res = requests.get(current_url, timeout=10)
    except requests.RequestException as e:
        print(f"アクセスに失敗しました：{current_url} ({e})")
        continue

    print(f"ステータスコード：{res.status_code}")
    print(f"ステータスメッセージ：{res.reason}")

    #飛ばす
    if res.status_code != 200:
        continue

    res.encoding = res.apparent_encoding

    #HTMLとして認識できないものをスキップ
    try:
        html_soup = BeautifulSoup(res.text, 'html.parser')
    except ParserRejectedMarkup:
        print(f"解析できないため、スキップ：{current_url}")
        continue

    title_tag = html_soup.find('title')

    #URLをキー、タイトルはバリュー
    title_tag = html_soup.find('title')
    if title_tag is not None:
        site_map[current_url] = title_tag.get_text(strip=True)
    else:
        site_map[current_url] = ''

    #同一ドメイン内のリンクにいってらっしゃい
    tag_href_list = html_soup.find_all('a', href=True)
    
    #リンク→URL
    for tag in tag_href_list:
        next_url = urljoin(current_url, tag.get('href'))
        next_url = urldefrag(next_url)[0]
        parsed_url = urlparse(next_url)

        if (
            parsed_url.scheme in ('http', 'https')
            and parsed_url.netloc == domain
            and next_url not in visited_url_set
            and next_url not in url_list
        ):
            url_list.append(next_url)

#CSVに入れる
with open('musashino_sitemap.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['URL', 'タイトル'])

    for page_url, page_title in site_map.items():
        writer.writerow([page_url, page_title])

#URLとタイトルのみを表示
for page_url, page_title in site_map.items():
    print(f"URL：{page_url} タイトル：{page_title}")
