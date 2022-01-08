# -*- coding: utf-8 -*-

import csv
import importlib
import os
import sys
import time
import random  # https://www.runoob.com/python/func-number-random.html  用法
from urllib.parse import quote  # 用于url编码解码

import re
import requests
from fake_useragent import UserAgent

importlib.reload(sys)
startTime = time.time()  # 记录起始时间

# --------------------------------------------文件存储-----------------------------------------------------
path = os.getcwd() + "./DoubleSubSpyder.csv"
csvfile = open(path, 'a', newline='', encoding='utf-8-sig')
writer = csv.writer(csvfile)
# csv列名
writer.writerow(('关键词', '微博链接', '博主id', '博主昵称', '博主账号等级', '博主性别',
                 '发博日期', '发博时间', '微博内容', '转发量', '评论量', '点赞量',
                 '评论者id', '评论者昵称', '评论者账号等级', '评论者性别', '评论日期', '评论时间', '评论内容', '点赞数'))
# 设置headers
headers = {
    'Cookie': '',  # 填写你的cookie
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


# --------------------------------------月份转换-----------------------------------------------
def trans_month(created_title_time):
    if 'Jan' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '01', created_title_time[2])
    elif 'Feb' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '02', created_title_time[2])
    elif 'Mar' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '03', created_title_time[2])
    elif 'Apr' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '04', created_title_time[2])
    elif 'May' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '05', created_title_time[2])
    elif 'Jun' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '06', created_title_time[2])
    elif 'Jul' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '07', created_title_time[2])
    elif 'Aug' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '08', created_title_time[2])
    elif 'Sep' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '09', created_title_time[2])
    elif 'Oct' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '10', created_title_time[2])
    elif 'Nov' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '11', created_title_time[2])
    elif 'Dec' in created_title_time:
        title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '12', created_title_time[2])
    else:
        pass
    return title_created_YMD


# -----------------------------------获取微博url------------------------------------------
def get_weibo_url(title1):
    topic = quote(title1, safe=";/?:@&=+$,", encoding="utf-8")

    for page in range(1, 106):  # 获取页数的范围
        headers = {
            "User-Agent": UserAgent().chrome,  # chrome浏览器随机代理
            'X-Requested-With': 'XMLHttpRequest'
        }
        api_url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D' + topic + '&page_type=searchall&page=' + str(page)
        print('当前url为：' + api_url)
        rep = requests.get(url=api_url, headers=headers)
        if not rep.json()['data']['cards']:  # 如果列表为空，也就是此页没有微博了，后面的直接跳过
            print('当前是第', page, '页，已经没内容了')
            break

        # 获取微博详情页的url
        for card in rep.json()['data']['cards']:
            if card['card_type'] == 9:
                weibo_url = card['scheme']
                weibo_url.translate(str.maketrans('', '', '\\'))
                weibo_url = weibo_url[0:35]  # 微博url
                print("微博url：", weibo_url)
                get_weibo_content(title1, weibo_url)
            elif card['card_type'] == 11:  # =11则需要进入之后进一步寻找
                if 'card_group' in card:
                    card_group = card['card_group']
                else:
                    continue
                for card_g in card_group:
                    if card_g['card_type'] == 9:
                        weibo_url = card_g['scheme']
                        weibo_url.translate(str.maketrans('', '', '\\'))
                        weibo_url = weibo_url[0:35]  # 微博url
                        print("微博url：", weibo_url)
                        get_weibo_content(title1, weibo_url)
        time.sleep(random.randint(6, 15))
    csvfile.close()


# -------------------------------------获取微博相关内容-----------------------------------------
def get_weibo_content(title2, url):
    try:
        rep = requests.get(url=url, headers=headers)
        html_text = rep.text
        # 话题内容
        find_title = re.findall('.*?"text": "(.*?)",.*?', html_text)[0]
        title_text = re.sub('<(S*?)[^>]*>.*?|<.*? />', '', find_title)  # 正则匹配掉html标签
        print('微博内容：', title_text)
        # 博文id
        title_text_id = re.findall('.*?"bid": "(.*?)",.*?', html_text)[0]
        print("博文id：", title_text_id)
        # 楼主ID
        title_user_id = re.findall('.*?"id": (.*?),.*?', html_text)[1]
        print("博主id：", title_user_id)
        # 楼主昵称
        title_user_nickName = re.findall('.*?"screen_name": "(.*?)",.*?', html_text)[0]
        print("博主昵称：", title_user_nickName)
        # 楼主账号等级
        title_user_level = ''
        try:
            title_user_level = re.findall('.*?"mbrank": (.*?),.*?', html_text)[0]
            print("博主账号等级：", title_user_level)
        except Exception as e:
            print(e)
        # 楼主性别
        title_user_gender = re.findall('.*?"gender": "(.*?)",.*?', html_text)[0]
        if title_user_gender == 'm':
            title_user_gender = '男'
        elif title_user_gender == 'f':
            title_user_gender = '女'
        else:
            title_user_gender = ''
        print("博主性别：", title_user_gender)
        # 发布时间
        created_title_time = re.findall('.*?"created_at": "(.*?)".*?', html_text)[0].split(' ')
        # 日期
        title_created_YMD = trans_month(created_title_time)
        print("博文发布日期：", title_created_YMD)
        # 发布时间
        add_title_time = created_title_time[3]
        print("博文发布时间", add_title_time)
        # 转发量
        retweets_count = re.findall('.*?"reposts_count": (.*?),.*?', html_text)[0]
        print("转发量：", retweets_count)
        # 评论量
        comments_count = re.findall('.*?"comments_count": (.*?),.*?', html_text)[0]
        print("评论量：", comments_count)
        # 点赞量
        upers_count = re.findall('.*?"attitudes_count": (.*?),.*?', html_text)[0]
        print("点赞量", upers_count)
        position1 = (title2, url, title_user_id, title_user_nickName, title_user_level, title_user_gender,
                     title_created_YMD, add_title_time, title_text, retweets_count, comments_count, upers_count,
                     " ", " ", " ", " ", " ", " ", " ", " ")
        time.sleep(random.randint(1, 5))
        # 写入数据
        writer.writerow(position1)
    except:
        pass


if __name__ == '__main__':
    # 待搜索关键词
    title_list = ['双减', '三胎']  # 可以输入多个关键词

    for title in title_list:
        # 只爬取微博内容（不含评论）
        get_weibo_url(title)

    # 计算使用时间
    endTime = time.time()
    useTime = (endTime - startTime) / 60
    print("该次所获的信息一共使用%s分钟" % useTime)


