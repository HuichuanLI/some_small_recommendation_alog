import bs4
import os
import requests
import re
import time
from urllib import request
from bs4 import BeautifulSoup  # 引入“爬取.py”所需要的所有库


def fetchUrl_RMRB(url):
    '''
    功能：访问 人民日报url 的网页，获取网页内容并返回
    参数：目标网页的 url
    返回：目标网页的 html 内容
    '''
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text


def getPageList_RMRB(year, month, day):
    '''
    功能：获取人民日报当天报纸的各版面的链接列表
    参数：年，月，日
    '''
    url = 'http://paper.people.com.cn/rmrb/html/' + year + '-' + month + '/' + day + '/nbs.D110000renmrb_01.htm'
    # 在人民日报版面目录的链接中，“/year-month/day/” 表示日期，后面的 “_01” 表示这是第一版面的链接。
    html = fetchUrl_RMRB(url)
    bsobj = bs4.BeautifulSoup(html, 'html.parser')
    pageList = bsobj.find('div', attrs={'id': 'pageList'}).ul.find_all('div', attrs={'class': 'right_title-name'})
    linkList = []
    '''
    根据html分析可知，版面目录存放在一个
    id = “pageList” 的div标签下，class = “right_title1” 或 “right_title2” 的 div 标签中，
    每一个 div 表示一个版面
    '''
    for page in pageList:
        link = page.a["href"]
        url = 'http://paper.people.com.cn/rmrb/html/' + year + '-' + month + '/' + day + '/' + link
        linkList.append(url)
    return linkList


def getTitleList_RMRB(year, month, day, pageUrl):
    '''
    功能：获取报纸某一版面的文章链接列表
    参数：年，月，日，该版面的链接
    '''
    html = fetchUrl_RMRB(pageUrl)
    bsobj = bs4.BeautifulSoup(html, 'html.parser')
    titleList = bsobj.find('div', attrs={'id': 'titleList'}).ul.find_all('li')
    '''
    使用同样的方法，我们可以知道，文章目录存放在一个id = “titleList” 的div标签下的ul标签中，
    其中每一个li标签表示一篇文章
    '''
    linkList = []

    for title in titleList:
        tempList = title.find_all('a')
        # 文章的链接就在li标签下的a标签中
        for temp in tempList:
            link = temp["href"]
            if 'nw.D110000renmrb' in link:  # 筛选出文章链接抓取，去除版面其他无关内容的链接
                url = 'http://paper.people.com.cn/rmrb/html/' + year + '-' + month + '/' + day + '/' + link
                linkList.append(url)
    return linkList


def getContent_RMRB(html):
    '''
    功能：解析人民日报HTML 网页，获取新闻的文章内容
    参数：html 网页内容
    '''
    bsobj = bs4.BeautifulSoup(html, 'html.parser')
    # 获取文章
    '''
    内容进入文章内容页面之后,由网页分析知正文部分存放在 id = “ozoom” 的 div 标签下的 p 标签里。
    '''
    pList = bsobj.find('div', attrs={'id': 'ozoom'}).find_all('p')
    content = ''
    for p in pList:
        content += p.text + '\n'
    resp = content
    return resp


def saveFile_RMRB(content, path, filename):
    '''
    功能：将文章内容 content 保存到本地文件中
    参数：要保存的内容，路径，文件名
    '''
    # 如果没有该文件夹，则自动生成
    if not os.path.exists(path):
        os.makedirs(path)

    # 保存文件
    with open(path + filename, 'w', encoding='utf-8') as f:
        f.write(content)


def download_RMRB(year, month, day, destdir):
    '''
    功能：爬取《人民日报》网站 某年 某月 某日 的新闻内容，并保存在 指定目录下
    参数：年，月，日，文件保存的根目录
    '''
    pageList = getPageList_RMRB(year, month, day)
    for page in pageList:
        titleList = getTitleList_RMRB(year, month, day, page)
        for url in titleList:
            # 获取新闻文章内容
            html = fetchUrl_RMRB(url)
            content = 'URL:' + url + '\n' + getContent_RMRB(html)
            bsobj = bs4.BeautifulSoup(html, 'html.parser')
            title = bsobj.h3.text + bsobj.h1.text + bsobj.h2.text
            # 剔除title的可能对识别造成影响的字符
            title = title.replace(':', '')
            title = title.replace('"', '')
            title = title.replace('|', '')
            title = title.replace('/', '')
            title = title.replace('\\', '')
            title = title.replace('*', '')
            title = title.replace('<', '')
            title = title.replace('>', '')
            title = title.replace('?', '')
            title = title.replace('.', '')
            # 生成保存的文件路径及文件名
            path = destdir + '/'
            fileName = title + '.txt'

            # 保存文件
            saveFile_RMRB(content, path, fileName)


def fetchUrl_WY(url):
    '''
    功能：访问 网易社会url 的网页，获取网页内容并返回
    参数：目标网页的 url
    返回：目标网页的 html 内容
    '''
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text


def download_WY(title, url, year, month, day):
    '''
    功能：爬取网易社会网站某一URL当日的新闻内容，并保存在指定目录下
    参数：新闻标题，抓取的URL，年，月，日
    '''
    html = fetchUrl_WY(url)
    bsobj = bs4.BeautifulSoup(html, 'html.parser')
    title = title.replace(':', '')
    title = title.replace('"', '')
    title = title.replace('|', '')
    title = title.replace('/', '')
    title = title.replace('\\', '')
    title = title.replace('*', '')
    title = title.replace('<', '')
    title = title.replace('>', '')
    title = title.replace('?', '')
    title = title.replace('.', '')
    # 获取新闻的时间来源 class='post_time_source'
    time = bsobj.find('div', class_='post_time_source').text
    # 获取新闻正文内容
    tag = bsobj.find('div', class_='post_text').text
    file_name = r'./今日新闻/' + title + '.txt'
    file = open(file_name, 'w', encoding='utf-8')
    tag = tag.replace(' ', '')
    content = 'URL:' + url + '\n' + '发布时间：' + time + '\n' + tag
    # 写入文件
    file.write(content)


def downloads_WY():
    '''
    功能：爬取网易社会网站所有种子URL（URL数组）下的新闻内容，并保存在指定目录下
    参数：无
    '''
    urls = ['http://temp.163.com/special/00804KVA/cm_shehui.js?callback=data_callback',
            'http://temp.163.com/special/00804KVA/cm_shehui_02.js?callback=data_callback',
            'http://temp.163.com/special/00804KVA/cm_shehui_03.js?callback=data_callback']
    '''
    网易新闻的标题及内容是使用js异步加载的，单纯的下载网页源代码是没有标题及内容的
    我们可以在Network的js中找到我们需要的内容
    '''
    for url in urls:
        req = request.urlopen(url)
        res = req.read().decode('gbk')
        pat1 = r'"title":"(.*?)",'
        pat2 = r'"tlink":"(.*?)",'
        m1 = re.findall(pat1, res)
        news_title = []
        for i in m1:
            news_title.append(i)
        m2 = re.findall(pat2, res)
        news_url = []
        for j in m2:
            news_url.append(j)
        for i in range(0, len(news_url)):
            download_WY(news_title[i], news_url[i], year, month, day)


def fetchUrl_BD(url, headers):  # 爬取百度news所有url
    urlsss = []
    r = requests.get(url, headers=headers).text
    soup = BeautifulSoup(r, 'lxml')
    for i in soup.find_all('h3'):  # 文章标题存放在 h3 标签中
        urlsss.append(i.a.get('href'))
    return urlsss


def getContent_BD(urls, headers, year, month, day):  # 对抓取到的百度新闻连接的内容的操作
    # 先检查是否存在该文件夹
    if os.path.exists('./今日新闻/'):
        pass
    else:
        os.mkdir('./今日新闻/')
    for q in urls:
        try:
            time.sleep(2)  # 定时抓取
            r = requests.get(q, headers=headers).text
            soup = BeautifulSoup(r, 'lxml')
            for i in soup.find('div', class_="article-title"):  # 每章的标题
                if os.path.exists('./今日新闻/' + i.get_text() + '.txt'):  # 检查是否已存在该文件
                    continue  # 内容已经抓取过并存在文件夹中，不必再抓取
                else:
                    for i in soup.find('div', class_="article-title"):  # 每章的标题
                        title = i.get_text().replace(':', '')
                        title = title.replace('"', '')
                        title = title.replace('|', '')
                        title = title.replace('/', '')
                        title = title.replace('\\', '')
                        title = title.replace('*', '')
                        title = title.replace('<', '')
                        title = title.replace('>', '')
                        title = title.replace('?', '')
                        title = title.replace('.', '')
                        f = open('./今日新闻/' + title + '.txt', 'w', encoding='utf-8')
                    for i in soup.find_all('div', class_="article-source article-source-bjh"):  # 发布日期
                        aas = i.find(class_="date").get_text()
                        aad = i.find(class_="time").get_text()
                        aaf = 'URL:%s' % q
                        f.write(aaf + '\n')
                        f.write(aas)
                        f.write(aad + '\n')
                    for i in soup.find_all('div', class_="article-content"):  # 每章的内容
                        f.write(i.get_text())
                        f.close()
        except Exception as result:  # 处理异常抓取的情况，使程序继续爬取其他网页
            continue


def download_BD():  # 下载百度新闻的内容以文件形式保存
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
    url = 'https://news.baidu.com/widget?id=AllOtherData&channel=internet&t=1554738238830'
    getContent_BD(fetchUrl_BD(url, headers), headers, year, month, day)


if __name__ == '__main__':
    '''
    主函数：程序入口
    '''
    # 爬取指定日期的新闻
    newsDate = input('请输入要爬取的日期（格式如 20200101 ）:')

    year = newsDate[0:4]
    month = newsDate[4:6]
    day = newsDate[6:8]

    # 对想爬取收集的网站进行选择
    flag_RMRB = input('是否爬取人民日报？是-1 否-0：')
    if flag_RMRB == '1':
        download_RMRB(year, month, day, './今日新闻')
        print("人民日报爬取完成!")

    # flag_WY = input('是否爬取网易社会新闻？是-1 否-0：')
    # if flag_WY == '1':
    #     downloads_WY()
    #     print('网易社会抓取完成！')

    flag_BD = input('是否爬取百度新闻？是-1 否-0：')
    if flag_BD == '1':
        download_BD()
        print('百度新闻抓取完成！')
