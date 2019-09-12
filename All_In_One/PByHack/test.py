#coding=utf-8
import re
import requests
import random


# 设置代理
proxy_list = [
	{"http" : "124.88.67.81:80"},
    {"http" : "124.88.67.82:80"},
    {"http" : "124.88.67.83:80"},
    {"http" : "124.88.67.84:80"},
    {"http" : "124.88.67.85:80"}
]
proxy = random.choice(proxy_list)
print('The proxy is:'+str(proxy))

# 主程序
f = open('info.txt','a')
num = 0
for i in range(10):
	data = i + 1
	url = 'https://github.com/search?p='+str(data)+'&q=bl_info&type=Code'
	print(url)
	head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/61.0'}
	htmls = requests.get(url)#,headers = head,proxies=proxy)
	htmls.encoding = 'utf-8'
	html = htmls.content

	##正则匹配
	findtexts = re.findall('<h3>(.*?)</h3>',str(html),re.S)
	
	##找到关键词并写入文件
	print('For [ '+str(data)+' ] Page')
	for findtext in findtexts:
		findurl = re.findall('href="(.*?)">',findtext)
		for each in findurl:
			num += 1
			print('https://github.com'+each)
			f.writelines('https://github.com'+each+'\n')
print(num)
f.close()
