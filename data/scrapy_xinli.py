"""
    scrapy flair Ai
"""
import logging
import pickle
import re
import threading
import time

import execjs
import pandas as pd
import requests
import scrapy
from requests import RequestException
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.utils.log import configure_logging
from tqdm import tqdm

# 配置日志级别为ERROR
configure_logging({'LOG_LEVEL': 'ERROR'})

logging.basicConfig(format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
                    level=logging.INFO)
log = logging.getLogger(__name__)

headers = {
    'authority': 'www.xinli001.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'cache-control': 'max-age=0',
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


def extract_urls(items):
    output = []
    for s in items:
        # 使用正则表达式提取id
        match = re.search(r'qa/\d+', s)
        if match:
            _id = match.group().replace('qa/', '')
            output.append(_id)
    return output


class PageStorage:
    def __init__(self, file_name):
        self.key = "page_count"
        self.file_name = file_name

    def read_data(self):
        # 从本地文件中加载数据
        with open(self.file_name, 'rb') as f:
            data = pickle.load(f)
        return data[self.key]

    def write_data(self, data):
        # 将数据持久化存储到本地文件
        with open(self.file_name, 'wb') as f:
            pickle.dump({self.key: data}, f)


lock = threading.Lock()
max_concurrent_requests = 10


class CookieManager:
    def __init__(self, start_url):
        self.complete_cookie = {}
        self.expire_time = 0
        self.url = start_url
        with open('generate_cookies.js', 'r', encoding='utf-8') as f:
            acw_sc_v2_js = f.read()
            self.acw = execjs.compile(acw_sc_v2_js)

    def get_cookies(self):
        if self.expire_time < time.time():
            # 重新获取cookies
            self.generate_cookies()
        return self.complete_cookie

    def generate_cookies(self, response=None):
        complete_cookie = {}
        expire_time = int(time.time()) + 600
        if response is None:
            response = requests.get(url=self.url, headers=headers)
        # 获取cookies
        arg1 = re.findall("arg1='(.*?)'", response.text)[0]
        acw_sc__v2 = self.acw.call('getAcwScV2', arg1)
        complete_cookie.update({"acw_sc__v2": acw_sc__v2})
        self.update_cookies(complete_cookie, expire_time)

    def update_cookies(self, data, expire_time):
        self.expire_time = expire_time
        self.complete_cookie = data


class MySpider(scrapy.Spider):
    name = 'xinLiSpider'

    # allowed_domains = []
    page_count = 1
    page_storage = PageStorage("qa.pkl")

    start_urls = []

    auth_token = '&u_atoken=fec696bf-5525-4975-8133-19598bce1f56&u_asession=01Gor3RMrTJcnAk6XDEjii2N4KAnJSSaxGVPlqFuCatT-XBbC1MXWpRs7qiCe3wiyvu1YxCuvO-2X4x05YBF-X2tsq8AL43dpOnCClYrgFm6o&u_asig=05oMTEtiyDfGac8z8D-HX9R6JhiNo7nWGfnxdK5ohiY0YR9q_4FX9wCv4EpkWO-8K4nTPlkYEgXQ3V3HhiCnCzonNhDP47M3Lm8Xf44lJqTEMMIlBdKIx2jb2ykOSeeA-u0QXjVptf8Q60HvwrucZCHYZHaj2R5tPHdPzm7wHpGsPtgfhWymyE3k3vFm3KiyspksmHjM0JOodanL5-M1Qs1Q4bS8FrFvarBOqvk6Ko2Rba-giG2Wg9YNjFQ-4iH5yD6JT4BsKufxGWJsij9GFddtZ_lqYXc2mQOawjXPzbberUpLHxH1iRKZmnjAu0Zefw&u_aref=XF%2FtBmP9i4JNkN%2Fx9K%2FaZhXUZm8%3D'

    prefix_url = 'https://www.xinli001.com/qa?page={}&type=question&object_name=last&title=&level2_tag=0&sort=id&from' \
                 '=houye-dh' + auth_token

    cookies = 'acw_tc=0b63bb6e17035738810702043e93c45982a97370541f59a22d774a52efd0a4; acw_sc__v3=658a798f6c8f218cd372a538cba4a4d2b2d368ca; log_session_id=eyJpdiI6Imd6azRHOE9sQmZsRjhLU2F4Nm9ScGc9PSIsInZhbHVlIjoiYjMxcUNzWWwySVB2SWJyRFRwdFhZSU9rQXhKNzVmMCttQksyc2w4bjZFND0iLCJtYWMiOiI4MjMwYjRhMWQ4MGMyNjE2M2JkY2E2MzgzYmM4ZTQ1YjNhNmRjMzI3YmM4MTFjNzk0YjdhZGE1OTllMmIwNWU0In0%3D; zg_did=%7B%22did%22%3A%20%2218ca4eadbde1e3-08206f98c6a0ea-26001951-144000-18ca4eadbdf746%22%7D; zg_18f5038ab49c4ae4918641ae36d67496=%7B%22sid%22%3A%201703573904356%2C%22updated%22%3A%201703573904356%2C%22info%22%3A%201703573904357%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.xinli001.com%22%7D; Hm_lvt_d64469e9d7bdbf03af6f074dffe7f9b5=1701326230,1703140851,1703490805,1703561412; Hm_lpvt_d64469e9d7bdbf03af6f074dffe7f9b5=1703573904; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218ca4eadc90461-0e3b58d8517873-26001951-1327104-18ca4eadc9162d%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThjYTRlYWRjOTA0NjEtMGUzYjU4ZDg1MTc4NzMtMjYwMDE5NTEtMTMyNzEwNC0xOGNhNGVhZGM5MTYyZCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218ca4eadc90461-0e3b58d8517873-26001951-1327104-18ca4eadc9162d%22%7D; sajssdk_2015_cross_new_user=1; laravel_session=eyJpdiI6ImRrYUdFQUQwR2xLZEVaaTE2VUpEWUE9PSIsInZhbHVlIjoibU1YTzFtNlM4cENDRU5uTlhwcGVCWWF5WkV3U3FQam5SMFVVVkxtcWJWWW9wRjZwRXJjMGFDUmZkbUxhXC8zTm9LT3dlREp1alA5UUgycyt1M2taSGxRPT0iLCJtYWMiOiJlMDBjMDdkN2NhMGU4OWE5NzA0N2I0MjdjNWNiZGYzOWMwYWMwMTU4MGMyZDI2YjllZTcwZGZlMTg1M2E4ZTkyIn0%3D'

    latest_id = None

    def __init__(self, output="questions.csv"):
        logging.info(f"init spider {self.name}")
        try:
            # self.page_count = self.page_storage.read_data()
            self.page_count = 1
        except FileNotFoundError:
            logging.error('page storage not found. Skipping...')
        self.start_urls = [self.prefix_url.format(self.page_count)]
        if output is not None:
            # 读取CSV文件
            df = pd.read_csv(output)
            if len(df) > 0:
                # 选择第一行中名为'column_name'的列
                self.latest_id = int(df.loc[0]['question_id'])

    def start_requests(self):
        # 设置要发送的请求和自定义 cookies
        yield scrapy.Request(self.start_urls[0], self.parse)
        # response = requests.get(self.start_urls[0], headers={
        #     'authority': 'www.xinli001.com',
        #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        #     'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        #     'cache-control': 'max-age=0',
        #     'cookie': 'acw_tc=0b63bb6e17035738810702043e93c45982a97370541f59a22d774a52efd0a4; acw_sc__v3=658a798f6c8f218cd372a538cba4a4d2b2d368ca; log_session_id=eyJpdiI6Imd6azRHOE9sQmZsRjhLU2F4Nm9ScGc9PSIsInZhbHVlIjoiYjMxcUNzWWwySVB2SWJyRFRwdFhZSU9rQXhKNzVmMCttQksyc2w4bjZFND0iLCJtYWMiOiI4MjMwYjRhMWQ4MGMyNjE2M2JkY2E2MzgzYmM4ZTQ1YjNhNmRjMzI3YmM4MTFjNzk0YjdhZGE1OTllMmIwNWU0In0%3D; Hm_lvt_d64469e9d7bdbf03af6f074dffe7f9b5=1701326230,1703140851,1703490805,1703561412; sajssdk_2015_cross_new_user=1; zg_did=%7B%22did%22%3A%20%2218ca4eadbde1e3-08206f98c6a0ea-26001951-144000-18ca4eadbdf746%22%7D; zg_18f5038ab49c4ae4918641ae36d67496=%7B%22sid%22%3A%201703573904356%2C%22updated%22%3A%201703574096661%2C%22info%22%3A%201703573904357%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.xinli001.com%22%7D; Hm_lpvt_d64469e9d7bdbf03af6f074dffe7f9b5=1703574097; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218ca4eadc90461-0e3b58d8517873-26001951-1327104-18ca4eadc9162d%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThjYTRlYWRjOTA0NjEtMGUzYjU4ZDg1MTc4NzMtMjYwMDE5NTEtMTMyNzEwNC0xOGNhNGVhZGM5MTYyZCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218ca4eadc90461-0e3b58d8517873-26001951-1327104-18ca4eadc9162d%22%7D; laravel_session=eyJpdiI6IlFnOXhDQktuU2U3QTBJOHRRck5VRmc9PSIsInZhbHVlIjoiVzJlZmRmRWNlNXZEUTlFdUFtZ0RYSktuVmRvUXFZeHErc29DeUxIeUJmdUQwcmw1NlFRbHBuTng2TTNsKzN1V0RIZmQrTFljZlZjVGt2alY1OG5cL0N3PT0iLCJtYWMiOiI0Zjg1ODI4ZTk5YjNlMjFjZWQ4MDhkMWY2YzlkNGM4MjExMDMwMTg2YTdiODc1OGRjZDcyNjZiNGYzZmMxZmQwIn0%3D',
        #     'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        #     'sec-ch-ua-mobile': '?0',
        #     'sec-ch-ua-platform': '"Windows"',
        #     'sec-fetch-dest': 'document',
        #     'sec-fetch-mode': 'navigate',
        #     'sec-fetch-site': 'none',
        #     'sec-fetch-user': '?1',
        #     'upgrade-insecure-requests': '1',
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        # })
        # yield Selector(text=response.text)

    def parse(self, response):
        # 提取当前页面所有questionIds
        link_urls = response.xpath('//*[@id="left"]/ul/li/p/span/a/@href').getall()
        question_ids = extract_urls(link_urls)
        stop_flag = False
        for q_id in question_ids:
            if self.latest_id is not None and int(q_id) <= self.latest_id:
                stop_flag = True
                break
            yield {"page": self.page_count, "question_id": q_id}
        if stop_flag:
            return
        if len(question_ids) > 0:
            self.page_count += 1
            self.page_storage.write_data(self.page_count)
            next_url = self.prefix_url.format(self.page_count)
            yield scrapy.Request(next_url, self.parse, headers={
                'authority': 'www.xinli001.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'cache-control': 'max-age=0',
                # 'cookie': 'acw_tc=0b63bb6e17035738810702043e93c45982a97370541f59a22d774a52efd0a4; acw_sc__v3=658a798f6c8f218cd372a538cba4a4d2b2d368ca; log_session_id=eyJpdiI6Imd6azRHOE9sQmZsRjhLU2F4Nm9ScGc9PSIsInZhbHVlIjoiYjMxcUNzWWwySVB2SWJyRFRwdFhZSU9rQXhKNzVmMCttQksyc2w4bjZFND0iLCJtYWMiOiI4MjMwYjRhMWQ4MGMyNjE2M2JkY2E2MzgzYmM4ZTQ1YjNhNmRjMzI3YmM4MTFjNzk0YjdhZGE1OTllMmIwNWU0In0%3D; Hm_lvt_d64469e9d7bdbf03af6f074dffe7f9b5=1701326230,1703140851,1703490805,1703561412; sajssdk_2015_cross_new_user=1; zg_did=%7B%22did%22%3A%20%2218ca4eadbde1e3-08206f98c6a0ea-26001951-144000-18ca4eadbdf746%22%7D; zg_18f5038ab49c4ae4918641ae36d67496=%7B%22sid%22%3A%201703573904356%2C%22updated%22%3A%201703574096661%2C%22info%22%3A%201703573904357%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.xinli001.com%22%7D; Hm_lpvt_d64469e9d7bdbf03af6f074dffe7f9b5=1703574097; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218ca4eadc90461-0e3b58d8517873-26001951-1327104-18ca4eadc9162d%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThjYTRlYWRjOTA0NjEtMGUzYjU4ZDg1MTc4NzMtMjYwMDE5NTEtMTMyNzEwNC0xOGNhNGVhZGM5MTYyZCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218ca4eadc90461-0e3b58d8517873-26001951-1327104-18ca4eadc9162d%22%7D; laravel_session=eyJpdiI6IlFnOXhDQktuU2U3QTBJOHRRck5VRmc9PSIsInZhbHVlIjoiVzJlZmRmRWNlNXZEUTlFdUFtZ0RYSktuVmRvUXFZeHErc29DeUxIeUJmdUQwcmw1NlFRbHBuTng2TTNsKzN1V0RIZmQrTFljZlZjVGt2alY1OG5cL0N3PT0iLCJtYWMiOiI0Zjg1ODI4ZTk5YjNlMjFjZWQ4MDhkMWY2YzlkNGM4MjExMDMwMTg2YTdiODc1OGRjZDcyNjZiNGYzZmMxZmQwIn0%3D',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            # response = requests.get(next_url, headers={
            #    'authority': 'www.xinli001.com',
            #    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            #    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            #    'cache-control': 'max-age=0',
            #    'cookie': 'acw_tc=0b63bb6e17035738810702043e93c45982a97370541f59a22d774a52efd0a4; acw_sc__v3=658a798f6c8f218cd372a538cba4a4d2b2d368ca; log_session_id=eyJpdiI6Imd6azRHOE9sQmZsRjhLU2F4Nm9ScGc9PSIsInZhbHVlIjoiYjMxcUNzWWwySVB2SWJyRFRwdFhZSU9rQXhKNzVmMCttQksyc2w4bjZFND0iLCJtYWMiOiI4MjMwYjRhMWQ4MGMyNjE2M2JkY2E2MzgzYmM4ZTQ1YjNhNmRjMzI3YmM4MTFjNzk0YjdhZGE1OTllMmIwNWU0In0%3D; Hm_lvt_d64469e9d7bdbf03af6f074dffe7f9b5=1701326230,1703140851,1703490805,1703561412; sajssdk_2015_cross_new_user=1; zg_did=%7B%22did%22%3A%20%2218ca4eadbde1e3-08206f98c6a0ea-26001951-144000-18ca4eadbdf746%22%7D; zg_18f5038ab49c4ae4918641ae36d67496=%7B%22sid%22%3A%201703573904356%2C%22updated%22%3A%201703574096661%2C%22info%22%3A%201703573904357%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.xinli001.com%22%7D; Hm_lpvt_d64469e9d7bdbf03af6f074dffe7f9b5=1703574097; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218ca4eadc90461-0e3b58d8517873-26001951-1327104-18ca4eadc9162d%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThjYTRlYWRjOTA0NjEtMGUzYjU4ZDg1MTc4NzMtMjYwMDE5NTEtMTMyNzEwNC0xOGNhNGVhZGM5MTYyZCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218ca4eadc90461-0e3b58d8517873-26001951-1327104-18ca4eadc9162d%22%7D; laravel_session=eyJpdiI6IlFnOXhDQktuU2U3QTBJOHRRck5VRmc9PSIsInZhbHVlIjoiVzJlZmRmRWNlNXZEUTlFdUFtZ0RYSktuVmRvUXFZeHErc29DeUxIeUJmdUQwcmw1NlFRbHBuTng2TTNsKzN1V0RIZmQrTFljZlZjVGt2alY1OG5cL0N3PT0iLCJtYWMiOiI0Zjg1ODI4ZTk5YjNlMjFjZWQ4MDhkMWY2YzlkNGM4MjExMDMwMTg2YTdiODc1OGRjZDcyNjZiNGYzZmMxZmQwIn0%3D',
            #    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            #    'sec-ch-ua-mobile': '?0',
            #    'sec-ch-ua-platform': '"Windows"',
            #    'sec-fetch-dest': 'document',
            #    'sec-fetch-mode': 'navigate',
            #    'sec-fetch-site': 'none',
            #    'sec-fetch-user': '?1',
            #    'upgrade-insecure-requests': '1',
            #    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            # })
            # self.parse(Selector(text=response.text))


class AnswerSpider(scrapy.Spider):
    name = 'AnswerSpider'

    # allowed_domains = []
    page_count = 1
    start_urls = []
    # page_storage = PageStorage("answer.pkl")

    prefix_url = 'https://www.xinli001.com/qa/{}?page={}&from=houye-dh'  # 这里填入你的爬取URL

    def __init__(self, file_name="questions.csv", output_file="answers.csv"):
        self.file_name = file_name
        self.output = output_file
        self.df = pd.read_csv(self.file_name)
        question_id = self.df['question_id'][0]
        self.start_urls = [self.prefix_url.format(question_id, 1)]
        # 初始化cookies
        self.cookies = CookieManager(self.start_urls[0])

    def closed(self, reason):
        logging.info("spider close " + reason)
        # 将更新后的数据保存回CSV文件
        self.df.to_csv(self.file_name, index=False)

    def parse(self, response):
        # 初始化cookies
        self.cookies.generate_cookies(response)
        # 获取DataFrame的总行数
        total_rows = len(self.df.index)
        # 更新数据
        for index, row in tqdm(self.df.iterrows(), total=total_rows):
            if self.df.loc[index, 'status'] == "finished":
                continue
            question_id = self.df.loc[index, 'question_id']
            answers = self.request_next(question_id, 1)
            for item in answers:
                yield item
            self.df.loc[index, 'status'] = "finished"
            if index % 20 == 0:
                self.df.to_csv(self.file_name, index=False)
            time.sleep(1)

    @staticmethod
    def check_503_error(string):
        prefix = "https://static.xinli001.com/503-error.html"
        pattern = re.compile(f"^{prefix}")
        match = pattern.match(string)
        return match is not None

    def request_try(self, url, max_retries=5):
        # check cookies是否过期
        global lock
        with lock:
            for i in range(max_retries):
                complete_cookie = self.cookies.get_cookies()
                try:
                    logging.info(f"request {url}")
                    response = requests.get(url=url, headers=headers, cookies=complete_cookie, verify=False)
                    response.raise_for_status()
                    if response.status_code == 200:
                        if self.check_503_error(response.url):
                            time.sleep(5)
                            logging.info(f"503 error message for url {response.url}")
                            continue  # 如果返回数据包含错误信息，则继续下一次重试
                    time.sleep(1)
                    return response
                except RequestException as e:
                    logging.info(f"请求失败：{e}")
                    time.sleep(5)
                time.sleep(2 * i + 1)
                if i == max_retries - 1:
                    logging.error("重试次数已达上限")
            # 如果请求失败或返回数据不合适，返回None
        return None

    def request_next(self, question_id, page_no):
        next_page_url = self.prefix_url.format(question_id, page_no)
        response = self.request_try(url=next_page_url)
        selector = Selector(text=response.text)
        # 处理question
        question_data = self.parse_question(selector)
        # 处理answer
        answers_data = self.parse_answers(question_data, selector)
        # 当前页
        # for item in answers_data:
        #     yield item
        # Next分页
        if len(answers_data) >= 10:
            return answers_data + self.request_next(question_id, page_no=page_no + 1)
        return answers_data

    def parse_question(self, response):
        data_question_id = response.css('div#answer-text::attr(data-question-id)').get()
        # 提取title
        question_title = response.css('div.title h1::text').get()
        if question_title is None:
            logging.error("process error")
        # 提取text
        question_context = response.xpath('//*[@id="left"]/div[1]/p[2]/text()').get()
        if question_title == "":
            logging.error("extract question error get empty question title")
        if question_context == "":
            logging.error("extract question error get empty question title")
        # 输出提取的数据
        return {
            "question_id": data_question_id,
            "title": question_title,
            "context": question_context.strip()
        }

    def parse_answers(self, question_data, response):
        answers = response.xpath('//*[@id="left"]/ul/li')
        answer_datas = []
        for answer in answers:
            answer_score = int(answer.xpath('//div[@class="label"]//span[@class="answer_zan"]/a/font/text()').get())
            answer_text = "".join(answer.xpath('//div[@class="text"]//text()').getall()).strip()
            if answer_text == "":
                logging.error("extract answer error get empty answer")
            answer_data = {}
            answer_data.update(question_data)
            answer_data.update({
                "score": answer_score,
                "answer": answer_text
            })
            answer_data.update(question_data)
            answer_datas.append(answer_data)
        return answer_datas


c = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 '
                  'Safari/537.36',
    # save in file CSV, JSON or XML
    'FEED_FORMAT': 'csv',  # csv, json, xml
    'FEED_URI': 'questions.csv',  #

    # used standard FilesPipeline (download to FILES_STORE/full)
    'ITEM_PIPELINES': {'scrapy.pipelines.files.FilesPipeline': 1},

    # this folder has to exist before downloading
    'FILES_STORE': '.',
})

# c.crawl(MySpider)
# c.start()

# create a new CrawlerProcess
answerProcess = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 '
                  'Safari/537.36',
    # save in file CSV, JSON or XML
    # 'FEED_FORMAT': 'csv',  # csv, json, xml
    # 'FEED_URI': 'answers.csv',  #

    "FEEDS": {
        'items.json': {
            'format': 'json',
            # 'fields': ['price', 'name'],
            # 'item_filter': 'myproject.filters.MyCustomFilter2',
            # 'postprocessing': [MyPlugin1, 'scrapy.extensions.postprocessing.GzipPlugin'],
            # 'gzip_compresslevel': 5,
        },
    },

    # used standard FilesPipeline (download to FILES_STORE/full)
    'LOG_LEVEL': 'INFO'
})


answerProcess.crawl(AnswerSpider)
answerProcess.start()