import requests

url = 'https://www.instagram.com/'
headers = {
    'connection': 'close',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4384.0 Safari/537.36',
    'cookie': 'ig_did=10CA1A00-E933-4D79-895B-9BB314E8D49F; mid=YATwuAAEAAFh57j_4anIumq_aBA7; ig_nrcb=1; csrftoken=2MIampUTg7SSA3HAnFckh35hIlR4rcFa; ds_user_id=1432865061; sessionid=1432865061%3AX6WYgDuodGBuLy%3A22; rur=ATN; urlgen="{\"96.45.183.76\": 25820}:1l4F2p:cLK2BVrPEXKwMRR7rp5IyutF0bI"'
}

requests.DEFAULT_RETRIES = 5
proxies = {"https": "127.0.0.1:1087"}
response = requests.get(url, headers=headers, proxies=proxies)
if response.status_code == 200:
    print(response.text)
