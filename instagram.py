import os
import re
import sys
import json
import time
import random
import requests
from hashlib import md5
from pyquery import PyQuery as pq

url_base = 'https://www.instagram.com/'
# 修改第一条XHR请求的url中的after参数值
# cursor=QVFDNU1wRXA0YlQ0Y0VTWXlCbnUydWVxY20xU3FSeTR2MjZCNE9LbkhSYWplNE93SHBWRzVJNzEwQ0ZTNTk3WVJLNVZUakpuOUJfdXBYc2lFcUxtRUVxMA==
uri = 'https://www.instagram.com/graphql/query/?query_hash=003056d32c2554def87228bc3fd9668a&variables=%7B%22id%22%3A%22{user_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D'

headers = {
    'connection': 'close',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4384.0 Safari/537.36',
    'cookie': 'ig_did=10CA1A00-E933-4D79-895B-9BB314E8D49F; mid=YATwuAAEAAFh57j_4anIumq_aBA7; ig_nrcb=1; csrftoken=2MIampUTg7SSA3HAnFckh35hIlR4rcFa; ds_user_id=1432865061; sessionid=1432865061%3AX6WYgDuodGBuLy%3A22; rur=ATN; urlgen="{\"96.45.183.76\": 25820}:1l4F2p:cLK2BVrPEXKwMRR7rp5IyutF0bI"'
}


def get_html(url):
    try:
        requests.DEFAULT_RETRIES = 5
        proxies = {"https": "127.0.0.1:1087"}
        response = requests.get(url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            return response.text
        else:
            print('请求网页源代码错误, 错误状态码：', response.status_code)
    except Exception as e:
        print(e)
        return None


def get_json(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print('请求网页json错误, 错误状态码：', response.status_code)
    except Exception as e:
        print(e)
        time.sleep(60 + float(random.randint(1, 4000)) / 100)
        return get_json(url)


def get_content(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            print('请求照片二进制流错误, 错误状态码：', response.status_code)
    except Exception as e:
        print(e)
        return None


def get_urls(html):
    urls = []
    user_id = re.findall('"profilePage_([0-9]+)"', html, re.S)[0]
    print('user_id：' + user_id)
    doc = pq(html)
    items = doc('script[type="text/javascript"]').items()
    for item in items:
        if item.text().strip().startswith('window._sharedData'):
            js_data = json.loads(item.text()[21:-1])
            edges = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
            page_info = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"][
                'page_info']
            cursor = page_info['end_cursor']
            flag = page_info['has_next_page']
            for edge in edges:
                if edge['node']['display_url']:
                    display_url = edge['node']['display_url']
                    print(display_url)
                    urls.append(display_url)
            print(cursor, flag)
    while flag:
        url = uri.format(user_id=user_id, cursor=cursor)
        print("--------------", url)
        js_data = get_json(url)
        infos = js_data['data']['user']['edge_owner_to_timeline_media']['edges']
        cursor = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        flag = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
        for info in infos:
            if info['node']['is_video']:
                video_url = info['node']['video_url']
                if video_url:
                    print(video_url)
                    urls.append(video_url)
            else:
                if info['node']['display_url']:
                    display_url = info['node']['display_url']
                    print(display_url)
                    urls.append(display_url)
        print(cursor, flag)
        # time.sleep(4 + float(random.randint(1, 800))/200)    # if count > 2000, turn on
    return urls


def main(user):
    url = url_base + user + '/'
    print("--------------", url)
    html = get_html(url)
    urls = get_urls(html)
    dirpath = r'.\{0}'.format(user)
    print("--------------", dirpath)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    for i in range(len(urls)):
        print('\n正在下载第{0}张： '.format(i) + urls[i], ' 还剩{0}张'.format(len(urls) - i - 1))
        try:
            content = get_content(urls[i])
            endw = 'mp4' if r'mp4?_nc_ht=scontent' in urls[i] else 'jpg'
            file_path = r'.\{0}\{1}.{2}'.format(user, md5(content).hexdigest(), endw)
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    print('第{0}张下载完成： '.format(i) + urls[i])
                    f.write(content)
                    f.close()
            else:
                print('第{0}张照片已下载'.format(i))
        except Exception as e:
            print(e)
            print('这张图片or视频下载失败')


if __name__ == '__main__':
    user_name = sys.argv[1]
    start = time.time()
    main(user_name)
    print('Complete!!!!!!!!!!')
    end = time.time()
    spend = end - start
    hour = spend // 3600
    minu = (spend - 3600 * hour) // 60
    sec = spend - 3600 * hour - 60 * minu
    print(f'一共花费了{hour}小时{minu}分钟{sec}秒')
