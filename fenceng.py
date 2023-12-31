import pandas as pd
import jieba
from snownlp import SnowNLP
import csv
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib.pyplot import rcParams 
import matplotlib.dates as mdate
import warnings
from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec
import nltk
import numpy as np
import multiprocessing #多进程模块
# 清洗文本
def clearTxt(line:str):
    if(line != ''):
        line = line.strip()
        # 去除文本英文和数字
        line = re.sub("[a-zA-Z0-9]", "", line)
        # 去除文本中文符号和英文符号
        line = re.sub("[\s+\.\!\/_,$%^*(+\"\'；：“”．]+|[+——！，。？?、~@#￥%……&*（）]+", "", line)
        return line
    return None

#文本切割
def sent2word(line):
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
    # print(word_cut)
    segSentence = ''
    for word in word_cut:
        if word != '\t':
            segSentence += word + " "
    return segSentence.strip()

#数据清洗
def cleandata(data):
    # 清洗文本
    clean_data = [item for item in data]
    clean_data = [clearTxt(item) for item in clean_data]
    clean_data = [sent2word(item) for item in clean_data]
    return clean_data



#情感分析SnowNLP
def emotion(words, gettime):
# 评论情感分析
    D=[]
    for i in range(len(words)):
        s=SnowNLP(words[i])
        k=s.summary(1)
        t=s.sentiments
        # print(t)
        a=[gettime[i],k,t]
        D.append(a)
    # print(D)
    with open('emotion.csv','a',encoding='utf-8-sig',newline='')as f1:
        write=csv.writer(f1)
        write.writerows(D)

#算出每天情感评分均值
    data=pd.read_csv("1.csv",header=None,names=["发布时间","中心句","情感分数"])
    timedata = data['发布时间'].copy()
    time = []
    for i in range(len(data)):
        timedata[i]=timedata[i][:10]
    data['发布时间']=timedata
    # Convert the date to datetime64
    timedatas = pd.to_datetime(timedata, format='%Y-%m-%d')
    data1 = data['情感分数'].groupby(timedatas).mean()
    # print(data1)
    df = {'发布时间':data1.index,'情感分数':data1.values}
    DF = pd.DataFrame(df)

    rcParams['font.sans-serif'] = 'kaiti'# 防止中文乱码
    warnings.filterwarnings('ignore', category=FutureWarning)
    data=pd.read_csv("1.csv",header=None,names=["发布时间","中心句","情感分数"])
    timedata = data['发布时间'].copy()
    for i in range(len(data)):
        timedata[i]=timedata[i][:10]
    data['发布时间']=timedata
    # Convert the date to datetime64
    timedatas = pd.to_datetime(timedata, format='%Y-%m-%d')
    data1 = data['情感分数'].groupby(timedatas).mean()
    # print(data1)
    df = {'发布时间':data1.index,'情感分数':data1.values}
    DF = pd.DataFrame(df)
    # print(DF)
    # print(DF['发布时间'])
    # print(DF['情感分数'])
    return DF

#计算tf-idf权值
def compute(clean_data):
    # 将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer()
    # 统计每个词语的tf-idf权值
    tf_idf_transformer = TfidfTransformer()
    # 将文本转为词频矩阵并计算tf-idf
    tfidf = tf_idf_transformer.fit_transform(vectorizer.fit_transform(clean_data))
    weight = tfidf.toarray()#权值
     # 获取词袋模型中的所有词语
    word = vectorizer.get_feature_names_out()
    print( "词频矩阵为：\n",weight)
    _w = np.nonzero(weight)
    x1 = _w[0]
    x2 = _w[1]
    tfidf_dict = {}
    for i in range(len(x1)):
        index = x2[i]
        tfidf_dict[word[index]] = weight[x1[i]][x2[i]]
    
    x=vectorizer.fit_transform(clean_data)
    # print('输出词袋内容：\n',x)
    word = sorted(vectorizer.vocabulary_.items(), key=lambda x: x[1], reverse=True)[:10]
    # print('输出词频前十的词：\n',word)
    return tfidf, tfidf_dict

#文本词语转词频矩阵，文本数据做聚类
def  kmeansPlot(data, tfidf, num):
    tfidf_array = tfidf.toarray()
    # kmeans聚类
    clf = KMeans(n_clusters=num, n_init='auto')
   #预测聚类结果
    result = clf.fit(tfidf_array).predict(tfidf_array)
    # tfidf_array = np.float64(tfidf_array)
    result_list  = list(result)
    print('预测聚类结果名单为：\n',result_list)
    #中心点
    # print(len(clf.cluster_centers_))#对于矩阵来说len是行
    print("输出中心点：\n",clf.cluster_centers_)#每一类的中心点
 
    #聚类评估指标，距离越小说明簇分的越好
    print("计算簇中某一点到簇中距离的和: \n",clf.inertia_)
    print("每个点所属簇标签: \n",clf.labels_)

    k_result = pd.DataFrame(())
    k_result["data"] = data
    k_result["label"] = result_list
    k_result.to_csv('./data/k_result.csv')
    return None

# 聚类结果可视化
def kmeansview(num, tfidf):
    tfidf_array = tfidf.toarray()
    colors_list = ['teal', 'skyblue', 'tomato', 'black']
    labels_list = ['0', '1', '2', '3']
    markers_list = ['o', '*', 'D', '1']  # 分别为圆、星型、菱形
    #画中心点
    # for i in range(num):
    #     plt.scatter(clf.cluster_centers_[i], clf.cluster_centers_[i], s=300, c=colors_list[i],
    #         label=labels_list[i], marker=markers_list[i])
    # plt.show()
    for i in range(num):
         plt.scatter(tfidf_array[i], tfidf_array[i], c=colors_list[i],
            label=labels_list[i], marker=markers_list[i])
    plt.show()
    return  None

# 每天情感评分可视化
def emotionview(DF):
    # 导入轴数据
    time =DF['发布时间']
    data = DF['情感分数']
    # 创建一个画布
    fig = plt.figure(figsize=(12,9))
    # 在画布上添加一个子视图
    ax = plt.subplot(111)
    # 这里很重要  需要将x轴的刻度 进行格式化
    ax.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d'))
    # 为X轴添加刻度
    plt.xticks(DF['发布时间'],rotation=45)
    plt.yticks(DF['情感分数'],rotation=20)
    # 画折线
    ax.plot(time,data,color='r')
    # 设置标题
    ax.set_title('折线图示例')
    # 设置 x y 轴名称
    ax.set_xlabel('日期',fontsize=20)
    ax.set_ylabel('情感',fontsize=20)
    plt.show()
    return None

# 训练word2vec_CBOW模型
def train_word2vec_CBOW(clean_data):
    model=Word2Vec(clean_data,vector_size=300,window=8,min_count=10,sample=1e-3, workers=multiprocessing.cpu_count(),sg=0)
    model.save("./word2vec_CBOW")
    model.wv.save_word2vec_format("./word2vec_CBOW_format", binary=False)
    print("word2vec_CBOW completed")
    return None

# 训练word2vec_skip_gram模型
def train_word2vec_skip_gram(clean_data):
    model=Word2Vec(clean_data,vector_size=300,window=8,min_count=10,sample=1e-3, workers=multiprocessing.cpu_count(),sg=1)
    model.save("./word2vec_skip_gram")
    model.wv.save_word2vec_format("./word2vec_skip_gram_format", binary=False)
    print("word2vec_skip_gram completed")
    return None

# word2vec_CBOW + tfidf加权训练词向量
def get_word2vec_CBOW_with_tif(tfidf_dict):
    word2vec_CBOW_model = Word2Vec.load('./word2vec_CBOW')
    key = [word for word in word2vec_CBOW_model.wv.key_to_index.keys()]
    w_CBOW_index = {}
    CBOW_vector = {}
    embeddings_matrix_CBOW = np.zeros((len(key) + 1, word2vec_CBOW_model.vector_size))
    print(len(key))
    for i in range(len(key)):
        try:
            word = key[i]
            w_CBOW_index[word] = i + 1
            CBOW_vector[word] = word2vec_CBOW_model.wv[word]
            if word in tfidf_dict.keys():
                embeddings_matrix_CBOW[i + 1] = word2vec_CBOW_model.wv[word] * tfidf_dict[word]
            else:
                embeddings_matrix_CBOW[i + 1] = word2vec_CBOW_model.wv[word]
        except:
            embeddings_matrix_CBOW[i + 1] = 0
    return w_CBOW_index, CBOW_vector, embeddings_matrix_CBOW

# word2vec_skip_gram + tfidf加权训练词向量
def get_word2vec_skip_gram_with_tif(tfidf_dict):
    word2vec_CBOW_model = Word2Vec.load('./word2vec_skip_gram')
    key = [word for word in word2vec_CBOW_model.wv.key_to_index.keys()]
    w_skip_gram_index = {}
    skip_gram_vector = {}
    embeddings_matrix_skip_gram = np.zeros((len(key) + 1, word2vec_CBOW_model.vector_size))
    for i in range(len(key)):
        try:
            word = key[i]
            w_skip_gram_index[word] = i + 1
            skip_gram_vector[word] = word2vec_CBOW_model.wv[word]
            if word in tfidf_dict.keys():
                embeddings_matrix_skip_gram[i + 1] = word2vec_CBOW_model.wv[word] * tfidf_dict[word]
            else:
                embeddings_matrix_skip_gram[i + 1] = word2vec_CBOW_model.wv[word]
        except:
            embeddings_matrix_skip_gram[i + 1] = 0
    return w_skip_gram_index, skip_gram_vector, embeddings_matrix_skip_gram

# 输出相近词
def calculate_most_similar(self, word):
    similar_words = self.wv.most_similar(word)
    print(word)
    for term in similar_words:
        print("相近词为：\n",term[0], term[1])
    return None

# 查看基于CBOW和skip_gram模型输入词的相近词
def show_similar():
    model_CBOW = Word2Vec.load('./word2vec_CBOW')
    print("查看基于word2vec_CBOW模型的相近词")
    calculate_most_similar(model_CBOW, "军")
    
    model_skip_gram = Word2Vec.load('./word2vec_skip_gram')
    print("查看基于word2vec_skip_gram模型的相近词")
    calculate_most_similar(model_skip_gram, "军")
    return None

# 划分训练集和测试集
def devide():
    df=pd.read_csv("./data/k_result.csv")
    print("df = \n", df)
    X = np.array([df["data"].map(total_vector)]).reshape(-1, 134)
    y = np.array(df["label"])
    print("x shape =", X.shape)
    print("y shape =",y.shape)
    # 首先将数据集划分为训练集和测试集，其中test_size表示测试集所占比例
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    # 然后将训练集划分为训练集和验证集，其中validation_size表示验证集所占比例
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=42)
    print(X_train.shape)
    print(y_train.shape)
    print(X_test.shape)
    print(y_test.shape)
    return X_train, y_train, X_test, y_test

def total_vector(words):
    model = Word2Vec.load("./word2vec_skip_gram")
    vec = np.zeros(300).reshape((1, 300))
    for word in words:
        try:
            vec += model.wv[word].reshape((1, 300))
        except KeyError:
            continue
    return vec

if __name__ == "__main__":
    data=pd.read_csv("%23俄乌战争%23.csv")
    num = 4
    clean_data = cleandata(data['用户昵称'])
    # print("clean_data= \n",clean_data)
    train_word2vec_CBOW(clean_data)
    train_word2vec_skip_gram(clean_data)

    DF = emotion(data['用户昵称'], data['点赞数'])
    # 计算tf-idf权值
    tfidf, tfidf_dict = compute(clean_data)
    # 训练word2vec_CBOW + tfidf加权词向量
    word_CBOW_index, word_CBOW_vector, embedding_matrix_CBOW = get_word2vec_CBOW_with_tif(tfidf_dict)
    # 训练word2vec_skip_gram + tfidf加权词向量
    word_skip_gram_index, word_skip_gram_vector, embedding_matrix_skip_gram = get_word2vec_skip_gram_with_tif(tfidf_dict)
   
    kmeansPlot(clean_data, tfidf, num)
    kmeansview(num, tfidf)
    emotionview(DF)
    # 查看基于CBOW和skip_gram模型输入词的相近词
    show_similar()
    # devide()