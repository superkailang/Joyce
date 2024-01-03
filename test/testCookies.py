import re

import execjs
import requests

index_url = "https://www.xinli001.com/qa/100841534?page=1&from=houye-dh"
headers = {
    'authority': 'www.xinli001.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'cache-control': 'max-age=0',
    'referer': 'https://www.xinli001.com/qa/100841638?page=1&from=houye-dh',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 '
                  'Safari/537.36'
}


def get_complete_cookie():
    with open('generate_cookies.js', 'r', encoding='utf-8') as f:
        acw_sc_v2_js = f.read()

    complete_cookie = {}
    # 第一次不带参数访问首页，获取 acw_tc 和 acw_sc__v2
    response = requests.get(url=index_url, headers=headers)
    complete_cookie.update(response.cookies.get_dict())
    arg1 = re.findall("arg1='(.*?)'", response.text)[0]
    acw_sc__v2 = execjs.compile(acw_sc_v2_js).call('getAcwScV2', arg1)
    complete_cookie.update({"acw_sc__v2": acw_sc__v2})
    # 第二次访问首页，获取其他 cookies
    response2 = requests.get(url=index_url, headers=headers, cookies=complete_cookie)
    complete_cookie.update(response2.cookies.get_dict())
    return complete_cookie


get_complete_cookie()
