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
path = os.getcwd() + "./newSpyder.csv"
csvfile = open(path, 'a', newline='', encoding='utf-8-sig')
writer = csv.writer(csvfile)
# csv头部
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


# -----------------------------------获取关键词下每条微博的url------------------------------------------
def get_topic_id(title1):
    # 对中文进行url编码
    topic = quote(title1, safe=";/?:@&=+$,", encoding="utf-8")

    for page in range(1, 106):  # 获取页数的范围 最多只能获取到106页的
        headers = {
            "User-Agent": UserAgent().chrome
        }
        api_url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D' + topic + '&page_type=searchall&page=' + str(page)
        print('当前url为：' + api_url)
        rep = requests.get(url=api_url, headers=headers)
        if not rep.json()['data']['cards']:  # 如果列表为空，也就是此页没有微博了，后面的直接跳过
            break
        # 获取微博详情页的url
        for card in rep.json()['data']['cards']:
            if card['card_type'] == 9:
                weibo_url = card['scheme']
                weibo_url.translate(str.maketrans('', '', '\\'))
                weibo_url = weibo_url[0:35]
                main(title1, weibo_url)  # 爬取微博详情和评论
            elif card['card_type'] == 11:  # =11则需要进入之后进一步寻找
                card_group = card['card_group']
                for card_g in card_group:  # 进入card_group寻找有无type=9微博
                    if card_g['card_type'] == 9:
                        weibo_url = card_g['scheme']
                        weibo_url.translate(str.maketrans('', '', '\\'))
                        weibo_url = weibo_url[0:35]  # 微博url
                        main(title1, weibo_url)  # 爬取微博详情和评论
        time.sleep(random.randint(6, 15))
    csvfile.close()


# -----------------------------------爬取每条微博的详情页面------------------------------------------
def spider_weibo(topic, weibo_url):
    try:
        article_url = weibo_url
        print("文章链接：", article_url)
        rep = requests.get(url=article_url, headers=headers)
        html_text = rep.text
        # 话题内容
        find_title = re.findall('.*?"text": "(.*?)",.*?', html_text)[0]
        title_text = re.sub('<(S*?)[^>]*>.*?|<.*? />', '', find_title)  # 正则匹配掉html标签
        print("博文内容：", title_text)
        # 博文id
        title_text_id = re.findall('.*?"bid": "(.*?)",.*?', html_text)[0]
        print("博文id：", title_text_id)
        # 楼主ID
        title_user_id = re.findall('.*?"id": (.*?),.*?', html_text)[1]
        print("博主id：", title_user_id)
        # 楼主昵称
        title_user_NicName = re.findall('.*?"screen_name": "(.*?)",.*?', html_text)[0]
        print("博主昵称：", title_user_NicName)
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
        # 评论的可能最大页数
        comment_maxPage = int(int(comments_count) / 20)  # 每个ajax一次加载20条数据
        position1 = (topic, article_url, title_user_id, title_user_NicName, title_user_level, title_user_gender,
                     title_created_YMD, add_title_time, title_text, retweets_count, comments_count, upers_count,
                     " ", " ", " ", " ", " ", " ", " ", " ")
        # 写入数据
        writer.writerow(position1)

        # 评论id
        comment_id = re.findall('.*?"mid": "(.*?)",.*?', html_text)[0]
        print("评论id：", comment_id)

        comment_con = {}
        comment_con['comment_id'] = comment_id
        comment_con['comment_maxPage'] = comment_maxPage
        return comment_con
    except:
        pass


# -------------------------------------------------拼接url，获取评论信息---------------------------------------------------
def get_page(comment_id, m_id, id_type, page):
    params = {
        'max_id': m_id,
        'max_id_type': id_type
    }
    if page == 0:
        url = ' https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'.format(comment_id, comment_id)
    else:
        url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id={}&max_id_type=0'.format(comment_id, comment_id,
                                                                                                m_id)
    try:
        r = requests.get(url, params=params, headers=headers)
        if r.status_code == 200:
            return r.json()
    except requests.ConnectionError as e:
        print('error', e.args)
        pass


# -------------------------------------------------获取下一页url的max_id和max_id_type---------------------------------------------------
def parse_page(jsondata):
    if jsondata:
        items = jsondata.get('data')
        item_max_id = {}
        item_max_id['max_id'] = items['max_id']
        item_max_id['max_id_type'] = items['max_id_type']
        return item_max_id


# -------------------------------------------------分解json信息，获取评论相关内容，并写入---------------------------------------------------
def write_csv(jsondata):
    for json in jsondata['data']['data']:
        # 评论者ID
        user_id = json['user']['id']
        # 评论者昵称
        user_name = json['user']['screen_name']
        # 评论者账号等级
        user_level = json['user']['mbrank']
        # 用户性别,m表示男性，表示女性
        try:
            user_gender = json['user']['gender']
            if user_gender == 'm':
                user_gender = '男'
            elif user_gender == 'f':
                user_gender = '女'
            else:
                user_gender = ''
        except:
            user_gender = ''
            pass
        # 获取评论
        comments_text = json['text']
        comment_text = re.sub('<(S*?)[^>]*>.*?|<.*? />', '', comments_text)  # 正则匹配掉html标签
        # 评论点赞数
        like_count = json['like_count']
        # 评论时间
        created_times = json['created_at'].split(' ')
        created_YMD = trans_month(created_times)
        created_time = created_times[3]  # 评论时间时分秒
        position2 = (" ", " ", " ", " ", " ", " ",
                     " ", " ", " ", " ", " ", " ",
                     user_id, user_name, user_level, user_gender, created_YMD, created_time, comment_text, like_count)
        writer.writerow(position2)  # 写入数据


# -------------------------------------------------主函数---------------------------------------------------
def main(topic, weibo_url):
    # 爬取微博博文等相关信息
    comment_con = spider_weibo(topic, weibo_url)
    # 获取评论id及最大评论页数
    comment_id = comment_con['comment_id']
    comment_maxPage = comment_con['comment_maxPage']
    # 爬取微博评论等相关信息
    m_id = 0  #
    id_type = 0  #
    try:
        # 用评论数量控制循环
        for page in range(0, comment_maxPage):  # 爬取全部评论
            # 自定义函数-拼接url，获取返回内容
            jsondata = get_page(comment_id, m_id, id_type, page)
            # 有的评论不可见，需要判断一下返回值
            if jsondata['ok'] == 0:
                print("评论不可见或评论为空，无法获取")
                break
            # 自定义函数-写入CSV文件
            write_csv(jsondata)

            # 自定义函数-获取下一页评论的url的max_id和max_id_type
            results = parse_page(jsondata)
            time.sleep(random.randint(4, 6))
            m_id = results['max_id']
            id_type = results['max_id_type']

            # 从max_id上判断：若下一页为空，就直接返回
            if m_id == 0:
                break
        print("本条微博的评论爬取完毕")
    except Exception as e:
        print(e)
        pass
    time.sleep(random.randint(8, 15))


if __name__ == '__main__':
    # 待搜索关键词
    title_list = ['双减', '三胎']  # 可以输入多个关键词

    for title in title_list:
        # 只爬取微博内容（不含评论）
        get_topic_id(title)

    endTime = time.time()
    useTime = (endTime - startTime) / 60
    print("该次所获的信息一共使用%s分钟" % useTime)
