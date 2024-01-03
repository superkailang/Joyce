import scrapy
import requests

url = "https://www.xinli001.com/qa/100841638?page=1&from=houye-dh"

cookies = "log_session_id=eyJpdiI6Ino5UDZZODZSd1pOUkFyXC9vTWQzS3N3PT0iLCJ2YWx1ZSI6ImJVR2gyMkNTVFwvSUVQNmpWR24yTGdnWEhsc0ZcL1Q0SWNRNEk5WjJ4MlVaTT0iLCJtYWMiOiJiMDk0ODlkY2Q3ZWFkZDliOTViZjIwNzNkOWI5ZDM5OTJmYzRkNTAzZDEwNDEyNDI4M2E4MmE5NWMzYzQ4OGQzIn0%3D; Hm_lvt_d64469e9d7bdbf03af6f074dffe7f9b5=1701326230,1703140851; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218c8ba0cb9c58e-0c4c7be4300a1d-26001951-1327104-18c8ba0cb9d6c5%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThjOGJhMGNiOWM1OGUtMGM0YzdiZTQzMDBhMWQtMjYwMDE5NTEtMTMyNzEwNC0xOGM4YmEwY2I5ZDZjNSJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218c8ba0cb9c58e-0c4c7be4300a1d-26001951-1327104-18c8ba0cb9d6c5%22%7D; requestAsk=true; acw_tc=0b63bb6e17032273264511386e93c62ff78eef6b295c2265e05b4df8a79b79; zg_did=%7B%22did%22%3A%20%2218c8b9d1e73b5-0cd7e1a85bde1d-26001951-144000-18c8b9d1e74d7%22%7D; zg_18f5038ab49c4ae4918641ae36d67496=%7B%22sid%22%3A%201703225354256%2C%22updated%22%3A%201703227470327%2C%22info%22%3A%201703149379199%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.xinli001.com%22%2C%22zs%22%3A%200%2C%22sc%22%3A%200%2C%22firstScreen%22%3A%201703225354256%7D; Hm_lpvt_d64469e9d7bdbf03af6f074dffe7f9b5=1703227470; laravel_session=eyJpdiI6IjVuUDlDOTVnUXpndnRkVEhzTjRodWc9PSIsInZhbHVlIjoiS2llbDlDc3g0bVc1MXFwa1VIM2tuVnpnXC96cGhmdlU2cE9PdHdKcXVWcGxNaEZEVEJJS3kxODhHaEFHUHlJMkhnbUI1ZkNpQllMNmhlZWNxb2xTektRPT0iLCJtYWMiOiI2MzdjZGVlZWUyOWY5MTM3OTFlZmE0M2E2OGNjNzcxMjEzZjNjMmIzZDhmOTM0Zjg5NDUwMTAxMTZiMmViYWFkIn0%3D; acw_sc__v2=658531fe26906ba57a6a5e25969520e6d9b4a67f"

payload = {}
headers = {
    'authority': 'www.xinli001.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'cache-control': 'max-age=0',
    'cookie': cookies,
    'referer': 'https://www.xinli001.com/qa/100841638?page=1&from=houye-dh',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def start_requests():
    yield scrapy.Request(url, headers=headers, callback=parse)


def parse(response):
    # 处理响应
    html_text = response.text
    # 在这里进行你想要的处理操作，例如提取数据、跟踪链接等
    # ...


# start_requests()

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
