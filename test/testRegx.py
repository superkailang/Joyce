import re

# 你的字符串
s = "/qa/100841665?from=shouye"

# 使用正则表达式提取id
match = re.search(r'qa/\d+', s)
if match:
    id = match.group().replace('qa/', '')
    print(f"提取的id是：{id}")
else:
    print("没有找到匹配的id")