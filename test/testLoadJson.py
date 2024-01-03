import json

file_name = "./data/items.json"
# 打开JSON文件
start_line = 1

# 打开并读取文件
with open(file_name, 'r') as f:
    data = json.load(f)
    print(len(data))

with open(file_name, 'r') as file:
    # 逐行读取文件内容
    for line in file:
        if line != '[\n' and line != ']\n':
            # 使用json.loads()解析每一行
            try:
                data = json.loads(line[:-2])
            except Exception as err:
                print(start_line)
            # 打印解析后的数据
            # print(start_line)
        else:
            print(start_line)
        start_line = start_line + 1
