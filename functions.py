import re
import jieba
from snownlp import SnowNLP
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import matplotlib.pyplot as plt
import wordcloud as wc
import pandas as pd



def fenlei(request):
    '''情感分类'''

    # j = '#印尼官方回应中国游客巴厘岛遇害事件#】5月1日，位于印尼巴厘岛的洲际酒店发生一起惊悚的命案，两名中国游客不幸身亡。印尼旅游和创意经济部长在接受CGTN记者采访时表示，对中国游客遇害事件深感悲痛、深表哀悼，印尼警方正在全力调查该事件，并已形成初步报告。他还表示，#巴厘岛#警方与执法部门已经组成特别小组，将尽快调查到底、查明真相，坚决杜绝此类事件的再次发生。LCGTN记者团的微博'
    s = SnowNLP(request)
    print(s.sentiments)

    # for item in tqdm(WeiBo.objects.all()): # 按行读取数据
    #     emotion = '正向' if SnowNLP(item.content).sentiments >0.45 else '负向'
    #     WeiBo.objects.filter(id=item.id).update(emotion=emotion)

    # return JsonResponse({'status':1,'msg':'操作成功'} )


def clearTxt(line:str):
    '''清洗文本'''
    if(line != ''):
        line = line.strip()
        # 去除文本中的英文和数字
        line = re.sub("[a-zA-Z0-9]", "", line)
        # 去除文本中的中文符号和英文符号
        line = re.sub("[\s+\.\!\/_,$%^*(+\"\'；：“”．]+|[+——！，。？?、~@#￥%……&*（）]+", "", line)
        return line
    print("文本为空！")
    return None



def sent2word(line):
    '''文本切割'''
    segList = jieba.cut(line,cut_all=False)
    # 去停用词
    stopwords1 = [line.strip() for line in open("stopwords/baidu_stopwords.txt", 'r', encoding="utf-8").readlines()]
    stopwords2 = [line.strip() for line in open("stopwords/cn_stopwords.txt", 'r', encoding="utf-8").readlines()]
    stopwords3 = [line.strip() for line in open("stopwords/hit_stopwords.txt", 'r', encoding="utf-8").readlines()]
    stopwords4 = [line.strip() for line in open("stopwords/scu_stopwords.txt", 'r', encoding="utf-8").readlines()]
    stopwords1.extend(stopwords2)
    stopwords1.extend(stopwords3)
    stopwords1.extend(stopwords4)
    # print(stopwords1)
    word_cut = [i for i in segList if i not in stopwords1 and len(i)!=1]
    #print(word_cut)
    segSentence = ''
    for word in word_cut:
        if word != '\t':
            segSentence += word + " "
    return segSentence.strip()


def Cloud_words(words, path):
    if path != ' ' :
        '''# 生成词云'''
        # 引入字体
        # mask = np.array(Image.open('love.png'))
        # image_colors = ImageColorGenerator(mask)
        # 从文本中生成词云图
        cloud = wc.WordCloud(
                            font_path="/System/Library/fonts/PingFang.ttc",#设置字体 
                            background_color='white', # 背景色为白色
                            height=600, # 高度设置
                            width=900, # 宽度设置
                            scale=20, # 长宽拉伸程度程度设置为20
                            prefer_horizontal=0.0, # 调整水平显示倾向程度
                            max_font_size=100, #字体最大值 
                            max_words=1000, # 设置最大显示字数为2000
                            relative_scaling=0.3, # 设置字体大小与词频的关联程度为0.3
                            )
        # 绘制词云图
        mywc = cloud.generate(words)
        plt.imshow(mywc)
        plt.axis('off')
        if path != 'showonly' :
            mywc.to_file(path)


def plot_bar_normal(data,datax):
    '''简单的条形图'''
	# data：条形图数据
	# x:x轴坐标
	# path：图片保存路径

	# 创建x轴显示的参数（此功能在与在图像中x轴仅显示能被10整除的刻度，避免刻度过多分不清楚）
	# x_tick = list(map(lambda num: "" if num % 10 != 0 else num, x))

	# 创建一个分辨率为3000*100的空白画布
	# plt.figure(figsize=(100, 20), dpi=10)

	# # 设置x轴的说明
	# plt.xlabel('Classes', size=100)
	# # 设置y轴的说明
	# plt.ylabel('Number of data', size=100)

	# 打开网格线
	# plt.grid()
	# 绘制条形图
	# plt.bar(range(len(data)), data,  width=1)
	# # 显示x轴刻度
	# plt.xticks(range(len(data)), range(len(data)), size=100)
	# # 显示y轴刻度
	# plt.yticks(size=100)
	# 获取当前图像句柄
	# fig = plt.gcf()
	# plt.show()
	# 存储当前图像
	# fig.savefig(path)

    result = plt.bar(datax,data)
    plt.bar_label(result)
    for a,b in zip(datax,data):
        plt.text(a,b,b,ha='center',va='bottom')

    plt.show()


def splitdata(kmeans_result):
    '''
    分割数据集
    '''
    splitdata = []
    for i in range(len(kmeans_result['label'].unique())):
        a = kmeans_result[kmeans_result['label'] == i]
        splitdata.append(a)
    return splitdata


def clean_and_plot(data, pic_out_path,print_weight:bool):
    '''
    输入文本信息，以及云图输出路径；输出词频前10的词和处理后的用于聚类的数据
    '''
    clean_data = [item for item in data]
    # 清洗文本
    # print("清洗文本")
    clean_data = [clearTxt(item) for item in clean_data]
    #文本切割
    # print("文本切割")
    clean_data = [sent2word(item) for item in clean_data]
    if pic_out_path != ' ':
        print('画云图')
        Cloud_words(','.join(clean_data), pic_out_path)
    vectorizer = CountVectorizer()
    a = vectorizer.fit_transform(clean_data)
    x = vectorizer.get_feature_names_out()
    # print('输出词袋内容：\n',x)
    word = sorted(vectorizer.vocabulary_.items(), key=lambda x: x[1], reverse=True)[:10]
    print('输出词频前十的词：\n',word)

    tf_idf_transformer = TfidfTransformer()
    tfidf = tf_idf_transformer.fit_transform(a)
    # print("权重矩阵\n",tfidf)
    tfidf_matrix = tfidf.toarray()

    if print_weight == True:
        print("输出所有词的权重：\n")
        word = vectorizer.get_feature_names_out()
        for i in range(len(tfidf_matrix)):
            for j in range(len(word)):
                print(word[j],tfidf_matrix[i][j])
    
    return word,tfidf_matrix

def mykmeans(data, tfidf_matrix, n_clusters=5):
    '''
    聚类
    输入：
        data: 原始数据列  注意！！：是列
        tfidf_matrix: 用于聚类的数据矩阵
        n_clusters: 聚类类别个数
    输出:
        result: 数据以及聚类标签整合后的表格
        clf.inertia_: 簇的某一点到簇中心距离的和
    '''
    from sklearn.cluster import KMeans
    import warnings
    warnings.filterwarnings('ignore', category=FutureWarning)

    clf = KMeans(n_clusters)
    result_list = clf.fit(tfidf_matrix).predict(tfidf_matrix)
    # print(result_list)

    from sklearn.metrics import silhouette_score,calinski_harabasz_score 
    
    calinski_harabasz = [calinski_harabasz_score(tfidf_matrix, result_list)] # 指标越大越好
    # print("评价指标ch：\n",calinski_harabasz)
    #计算轮廓系数
    silhouette_avg = [silhouette_score(tfidf_matrix, result_list)]
    # print("聚类模型轮廓系数为：", silhouette_avg)

    evaluation = pd.DataFrame(())
    evaluation['calinski_harabasz_score'] = calinski_harabasz
    evaluation['silhouette_score'] = silhouette_avg

    result_list  = list(result_list)

    result = pd.DataFrame(())
    result["data"] = data
    result["label"] = result_list

    # print("输出中心点：\n",clf.cluster_centers_)#每一类的中心点
    # print("计算簇中某一点到簇中距离的和: \n",clf.inertia_)
    # print("每个点所属簇标签: \n",clf.labels_)



    return result, evaluation

def plotkmeans(tfidf_matrix, result_list, n_clusters):
    # 聚类结果可视化
    colors_list = ['teal', 'skyblue', 'tomato', 'black', 'green']
    labels_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    markers_list = ['o', '*', 'D', '1', '2']  # 分别为圆、星型、菱形

    pltdata = pd.DataFrame((tfidf_matrix))
    pltdata = pd.DataFrame((tfidf_matrix))

    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    pca.fit(pltdata)
    newX = pd.DataFrame((pca.fit_transform(pltdata)))
    print(newX)

    newX['label'] = result_list
    slplitdata = splitdata(newX)

    for i in range(n_clusters):
        plt.scatter(slplitdata[i][0], slplitdata[i][1], c=colors_list[i],
        label=labels_list[i], marker=markers_list[i])
    plt.show()

def plotlinechart(data):
    from matplotlib.pyplot import rcParams 
    import matplotlib.dates as mdate
    import numpy as np
    # 防止中文乱码
    # rcParams['font.sans-serif'] = 'kaiti'
    
    # 生成一个时间序列 
    # time =pd.to_datetime(np.arange(0,11), unit='D',
    #                 origin=pd.Timestamp('2023-07-01'))
    
    # 生成数据
    # data = np.random.randint(0,1,size=11)


    # 创建一个画布
    fig = plt.figure(figsize=(12,9))
    # 在画布上添加一个子视图
    ax = plt.subplot(111)

    # 画折线
    # ax.plot(data['n_clusters'],data['calinski_harabasz_score'],color='r')
    ax.plot(data['n_clusters'],data['silhouette_score'],color='b')
    # 设置标题
    ax.set_title('kmeans n_clusters and evaluation')
    # 设置 x y 轴名称
    ax.set_xlabel('n_clusters',fontsize=20)
    ax.set_ylabel('evaluation',fontsize=20)
    plt.show()