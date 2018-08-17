# !/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import os
from urllib.parse import urlencode
from  requests.exceptions import RequestException
# import pymongo
from jiepaiconfig import *
from hashlib import md5
from multiprocessing import Pool

# 链接数据库,加connent=Falses是因为之后要引入多进程避免出现警告
# client = pymongo.MongoClient(MONGO_URL,port=27017,connent=False)
# db = client[MONGO_DB]

# 网页起始点
GROUP_START =1
# 网页终止点
GROUP_END=10

def get_one_page(offset):
    params ={
        'offset': 'offset',
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3,
        'from': 'search_tab',
     }

    url = 'https://www.toutiao.com/search_content/?'+ urlencode(params)
    try:
            response = requests.get(url)
            if response.status_code ==200:
                return response.json()
            return None
    except RequestException:
           print("请求页出现错误")
           return None

def parse_page_index(json):
    # json.loads是将json文本字符转换为json对象，dumps()将json对象转换为文本字符串
    data = json.get('data')
    #保证data在里面
    if data:
        # 循环data取出article_url链接：
        for item in data:
            # print(item)
            image_list = item.get('image_list')
            title = item.get('title')
            # print(image_list)
            if image_list:
                for image in image_list:
                    yield {
                        'image': image.get('url'),
                        'title': title
                    }


# result 要存储的形参，本项目为结果定义为result
# def save_to_mongo(result):
#     # 判断是否储存成功
#     if db(MONGO_TABLE).insert(result):
#         print('存储到MONGODB成功',result)
#         return True
#     return False

# def download_image(url):
#     print("正在下载",url)
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             # content和text区别：content返回二进制内容，text返回常规内容
#             save_image(response.content)
#         return None
#     except RequestException:
#         print("请求图片错误", url)
#         return None

def save_image(item):
    if not os.path.exists(item.get('title')):
        os.mkdir(item.get('title'))
    try:
        local_image_url = item.get('image')
        new_image_url = local_image_url.replace('list', 'large')
        response = requests.get('http:' + new_image_url)
        if response.status_code == 200:
            # {0}/{1}.{2}表示存储到本地名称，0表示存储路径1表示存储名称2表示存储后缀,md5是防止重复
            file_path = '{0}/{1}.{2}'.format(item.get('title'), md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb')as f:
                    f.write(response.content)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to save image')

def main(offset):
    # 将get_one_page(offset,keyword)赋值为(0,"街拍")
    json = get_one_page(offset)
    # print(html)
    for item  in parse_page_index(json):
        print(item)
        save_image(item)
        # save_to_mongo(item)


if __name__ =="__main__":
    pool = Pool()
    groups =[x*20 for x in range(GROUP_START,GROUP_END+1)]
    pool.map(main,groups)
    pool.close()
    pool.join()