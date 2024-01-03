from collections import Counter


def process_array(arr):
    # 统计每个元素的出现次数
    count_dict = {}
    for num in arr:
        count_dict[num] = count_dict.get(num, 0) + 1

    # check
    total = count_dict[arr[0]]
    for num in arr:
        if count_dict.get(num) != total:
            # logging.err
            print("error list for field ", count_dict.get(num), total)

    # 根据出现次数过滤数组
    filtered_arr = []
    for num in arr:
        if num in count_dict:
            filtered_arr.append(num)
            del count_dict[num]  # 如果已经添加到结果数组中，则从计数字典中删除，避免重复添加

    return filtered_arr, total  # 返回去重后的数组和重复的次数


# 示例用法
arr1 = ["#974", "#973", "#974", "#973", "#974", "#973", "#974", "#973"]
arr2 = ["#13", "#12", "#13", "#12"]
arr3 = ["#16", "#14"]

print(process_array(arr1))  # 输出: [['#975'], 3]  
print(process_array(arr2))  # 输出: [['#12', '#13'], 2]  
print(process_array(arr3))  # 输出: [['#14', '#16'], 1]
