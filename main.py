from functions import *

import pandas as pd



#读取数据
print("读取数据")
# data = pd.read_csv('%23新冠肺炎%23.csv')
data = pd.read_csv('./%23俄乌战争%23.csv')
print(data.shape)

# 清除重复数据
print("清除重复数据")
data.drop_duplicates('用户昵称',keep='first',inplace=True)
print(data.shape)

print("清洗数据并画图")
word, clean_data = clean_and_plot(data['用户昵称'], './picture/fulldata.png', False)
plt.show()

# 第一层5分类
kmeans_result, evaluation = mykmeans(data['用户昵称'], clean_data, n_clusters=5)

print("画图")
plot_bar_normal(kmeans_result["label"].value_counts().values,kmeans_result["label"].value_counts().index)

print("按标签拆分数据集")
result = splitdata(kmeans_result)
print(len(result))

# 第二层五分类
kmean2_word = []
kmean2_clean_data = []
for i in range(len(result)):
    kmeanword, clean_data = clean_and_plot(result[i]['data'], './picture/kmean1_'+str(i)+'.png', False)
    plt.show()
    kmeans_result, evaluation  = mykmeans(result[i]['data'], clean_data, n_clusters=5)

    print("画图")
    plot_bar_normal(kmeans_result["label"].value_counts().values,kmeans_result["label"].value_counts().index)

    kmean2_word.append(kmeanword)
    kmean2_clean_data.append(clean_data)
