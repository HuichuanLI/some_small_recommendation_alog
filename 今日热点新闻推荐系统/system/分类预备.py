import os
import re

'''
“分类预备.py”程序 功能1：过滤新闻中除中文外所有字符，便于进行分类中的中文分词 
功能2：创建分类文件的保存路径，便于进行分类不同类别新闻归类保存
'''

path1 = './今日新闻/过滤'
if os.path.exists(path1):
    path1 = './今日新闻/过滤'
else:
    os.makedirs(path1)
path = './今日新闻'
dirs = os.listdir(path)
for fn in dirs:  # 循环读取路径下的新闻文件并筛选输出
    if os.path.splitext(fn)[1] == ".txt":  # 筛选txt文件
        print(fn)
        inputs = open(os.path.join('./今日新闻', fn), 'r', encoding='UTF-8')  # 加载要处理的文件的路径
        guolv = open(path + '/' + '过滤' + fn, 'w', encoding='UTF-8')
        for eachline in inputs:
            eachline = re.sub(u"([^\u4e00-\u9fa5])", "", eachline)  # 只保留汉字字符
            guolv.write(eachline)
        guolv.close()

for i in range(0, 50):  # 创建分类文件的保存路径，便于进行分类不同类别新闻归类保存
    if os.path.exists('./今日新闻/分类/' + 'label_' + str(i) + '/'):
        pass
    else:
        os.makedirs('./今日新闻/分类/' + 'label_' + str(i) + '/')
