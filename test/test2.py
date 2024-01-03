import pandas as pd

# 你的数据
data = [[1, 2], [2, 3, 4], [5]]

# 创建DataFrame
df = pd.DataFrame(data, columns=['A', 'B', 'C', 'D', 'E', 'F', 'G'])

# 将DataFrame写入Excel文件
df.to_excel('output.xlsx', index=False)