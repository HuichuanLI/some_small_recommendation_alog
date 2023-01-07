from urllib import request
import json
import sys
import time
import hashlib
import re
import codecs, sys
import mysql.connector
import re


def getResponse(url, pageindex):
    data = {"hotelId": 1551791, "pageIndex": pageindex, "tagId": 0, "pageSize": 10, "groupTypeBitMap": 2,
            "needStatisticInfo": 0, "order": 0, "basicRoomName": "", "travelType": -1,
            "head": {"cid": "09031179411625216472", "ctok": "", "cver": "1.0", "lang": "01", "sid": "8888",
                     "syscode": "09", "auth": "", "extension": []}}
    data = json.dumps(data).encode(encoding='utf-8')

    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                   "Content-Type": "application/json"}

    url_request = request.Request(url=url, data=data, headers=header_dict)
    print("这个对象的方法是：", url_request.get_method(), i)

    url_response = request.urlopen(url_request)

    return url_response


def filter_emoji(desstr, restr=""):
    # 过滤表情
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)


def into(path, string):
    conn = mysql.connector.connect(user='root', password='12345678', database='grades', use_unicode=True)
    cursor = conn.cursor()
    f = codecs.open(path, 'r', encoding='utf-8')
    f = f.read()
    f = filter_emoji(f, restr='')
    f = f.replace('\r', '')
    f = f.replace('\n', '')
    f = f.replace('"', "")
    f = f[0:100]
    print(f)
    # comment = str(bytes(f, encoding='utf-8').decode('utf-8').encode('gbk', 'ignore').decode('gbk'))sql
    try:
        print(string)
        print(f)
        cursor.execute('insert into grades (hotel,date) values(%s,%s)', [string, f])
        conn.commit()
    except:
        conn.rollback()
        print("fail")


if __name__ == "__main__":
    try:
        for i in range(1, 2):
            Comments = []
            http_response = getResponse(
                "http://m.ctrip.com/restapi/soa2/16765/gethotelcomment?_fxpcqlniredt=09031144211504567945", i)
            data = http_response.read().decode('utf-8')
            dic = json.loads(data)
            ungz = dic['othersCommentList']
            for k in range(10):
                content = ungz[k]
                comment = content['content']
                with open('./data/comment_examples2.txt', 'a', encoding='UTF-8') as f:
                    f.write(json.dumps(comment, ensure_ascii=False) + '\n')
            time.sleep(10)
        sourceFile1 = './data/comment_examples2.txt'
        string1 = "北京三元桥CitiGO欢阁酒店"
        into(sourceFile1, string1)
    except:
        sourceFile1 = './data/comment_examples2.txt'
        string1 = "北京三元桥CitiGO欢阁酒店"
        into(sourceFile1, string1)
