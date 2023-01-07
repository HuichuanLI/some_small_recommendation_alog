from django.shortcuts import render
from django.views.decorators import csrf
import mysql.connector
 
# 接收POST请求数据
def search_post(request):
	conn = mysql.connector.connect(user='root', password='12345678', database='grades', use_unicode=True)
	cursor = conn.cursor()
	ctx ={}
	if request.POST:
		res=request.POST['q']
		sql="SELECT * FROM grades WHERE hotel=%s"
		cursor.execute(sql,(res,))
		results = cursor.fetchall()
		results=results[0]
		grade=results[1]
		data=results[2]
		ctx['rlt1'] = "分数："+str(grade)
		ctx['rlt2']="评论："+str(data)+"......"
		cursor.close()
	return render(request, "hello.html", ctx)
