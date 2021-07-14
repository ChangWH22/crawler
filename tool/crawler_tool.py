import re
import requests as rq
import time
import os

def clean_html(file):
    file = re.sub(r"<[^>]+>", "", str(file))
    file = re.sub("\n", "", file)
    file = re.sub("\r", "", file)
    return file

def clean_txt(file):
    file = re.sub(r"[▲▼]", "", file)
    file = re.sub(r"\s{0,}\(.*?\)\s{0,}","",file)
    file = re.sub(r"\s{0,}\（.*?\）\s{0,}", "", file)
    file = re.sub(r"\s{0,}\《.*?\》\s{0,}", "", file)
    file = re.sub(r"\s{0,}", "", file)
    return file


def split_article(article):
    article = re.sub("\.\.\.","。",article)
    sp = re.split("。|；|\?|!|？|！|：|:",article)
    return (sp)


def url_retry(url, retry_time=1):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/52.0.2743.116 Safari/537.36'}
    try:
        response = rq.get(url, timeout=(5, 20), headers = headers)
        html = response.text
        return html

    except:
        trytimes = 10  # 重複連接

        if retry_time < trytimes:
            retry_time += 1
            time.sleep(1)
            print("reconnect %s time" % retry_time)
            return url_retry(url, retry_time)
        else:
            return "205512310000"

def url_retry_mops(url, retry_time=1):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/52.0.2743.116 Safari/537.36'}
    try:
        response = rq.get(url, timeout=(5, 20), headers=headers)
        return response

    except:
        trytimes = 10  # 重複連接

        if retry_time < trytimes:
            retry_time += 1
            time.sleep(1)
            print("reconnect %s time" % retry_time)
            return url_retry(url, retry_time)
        else:
            return "205512310000"



def url_retry_json(url, retry_time=1):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)'
                             ' Chrome/52.0.2743.116 Safari/537.36'}
    try:
        response = rq.get(url, timeout=(5, 20), headers=headers)
        html = response.json()
        return html

    except:
        trytimes = 10  # 重複連接

        if retry_time < trytimes:
            retry_time += 1
            time.sleep(retry_time)
            print("reconnect %s time" % retry_time)
            return url_retry(url, retry_time)
        else:
            return "205512310000"


def mkdir(location):

    path = "D:/User/Desktop/corpus/report/" + location
    if os.path.exists(path):
        print(path + '....目錄已存在')
    else:
        os.makedirs(path)
        print('-----建立成功-----')


