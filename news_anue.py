import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
import crawler.tool as crawler_tool
import datetime
import time
import random
from queue import Queue
import json
import re

def anue_GET_NEWS_time_threading(decide_time_begin, decide_time_end,q):
    dt = datetime.datetime.today() - datetime.datetime.fromtimestamp(1611763199)  # 1/27差值
    dta = (dt.days + 1) * 86400 + 1611763199
    dtb = str(dta - 11 * 86400 + 1)
    dta = str(dta)

    title = []
    publish_time = []
    section = []
    body = []
    source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    loop_flag = False

    for page in range(1, 30):
        print("start collecting Anue page {page}".format(page=page))
        home_url = "https://api.cnyes.com/media/api/v1/newslist/category/headline?limit=30&startAt="+dtb+"&endAt="+dta+"&page="\
                   + str(page)
        r = crawler_tool.url_retry_json(home_url)
        time.sleep(1)

        for i in range(len(r["items"]["data"])):

            content_url = "https://news.cnyes.com/news/id/"+str(r["items"]["data"][i]["newsId"])
            r2 = crawler_tool.url_retry(content_url)
            soup = BeautifulSoup(r2, "lxml")
            try:
                r_time = datetime.datetime.strptime(soup.find("time").string, "%Y/%m/%d %H:%M")

                if r_time > b_time:
                    continue

                elif r_time < e_time:
                    loop_flag = True
                    print("---Web Crawler has collected Anue data from {b_time} to {e_time}---".format(b_time=b_time, e_time=e_time))
                    break

                else:
                    section.append(soup.find("meta", attrs={"property": "og:title"})["content"].split("|")[-1].split("-")[-1])
                    title.append(re.sub(r"\s{1,}","",soup.find("meta", attrs={"property": "og:title"})["content"].split("|")[0]))
                    source.append(soup.find("meta", attrs={"property": "og:title"})["content"].split("|")[-1].split("-")[0])
                    publish_time.append(r_time)
                    body.append(crawler_tool.clean_html("".join(str(x) for x in soup.select("div._2E8y p"))))
                    print("Anue:", r_time)
                    time.sleep(random.uniform(0, 1.5))
            except:
                pass
        if loop_flag == True:
            break

    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body})
    file_name = "D:/User/Desktop/corpus/news/anue/" + decide_time_begin + "_" + decide_time_end + "_Anue.csv"
    df.to_csv(file_name, encoding="utf-8")
    q.put(df)

def anue_GET_NEWS_time(decide_time_begin, decide_time_end):
    dt = datetime.datetime.today() - datetime.datetime.fromtimestamp(1611763199)  # 1/27差值
    dta = (dt.days + 1) * 86400 + 1611763199
    dtb = str(dta - 11 * 86400 + 1)
    dta = str(dta)

    title = []
    publish_time = []
    section = []
    body = []
    source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    loop_flag = False

    dta = '1612108799' # end
    dtb = '1611936000' # beg
    for page in range(1, 30):
        print("start collecting Anue page {page}".format(page=page))
        home_url = "https://api.cnyes.com/media/api/v1/newslist/category/headline?limit=30&startAt="+dtb+"&endAt="+dta+"&page="\
                   + str(page)
        r = crawler_tool.url_retry_json(home_url)
        time.sleep(5)

        for i in range(len(r["items"]["data"])):

            content_url = "https://news.cnyes.com/news/id/"+str(r["items"]["data"][i]["newsId"])
            r2 = crawler_tool.url_retry(content_url)
            soup = BeautifulSoup(r2, "lxml")
            try:
                r_time = datetime.datetime.strptime(soup.find("time").string, "%Y/%m/%d %H:%M")

                if r_time > b_time:
                    continue

                elif r_time < e_time:
                    loop_flag = True
                    print("---Web Crawler has collected Anue data from {b_time} to {e_time}---".format(b_time=b_time, e_time=e_time))
                    break

                else:
                    section.append(soup.find("meta", attrs={"property": "og:title"})["content"].split("|")[-1].split("-")[-1])
                    title.append(re.sub(r"\s{1,}","",soup.find("meta", attrs={"property": "og:title"})["content"].split("|")[0]))
                    source.append(soup.find("meta", attrs={"property": "og:title"})["content"].split("|")[-1].split("-")[0])
                    publish_time.append(r_time)
                    body.append(crawler_tool.clean_html("".join(str(x) for x in soup.select("div._2E8y p"))))
                    print("Anue:", r_time)
                    time.sleep(random.uniform(0, 1.5))
            except:
                pass
        if loop_flag == True:
            break

    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body})
    file_name = "D:/User/Desktop/corpus/news/temporarily/" + decide_time_begin + "_" + decide_time_end + "_Anue.csv"
    df.to_csv(file_name, encoding="utf-8")

def trans_time(timeString):
    '''
    timeString:2021-01-30 0:0:0
    input (str): %yyyy-%mm-%dd %H:%M:%S
    output (str): '1611936000'
    '''
    import time

    struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S") # 轉成時間元組
    time_stamp = int(time.mktime(struct_time)) # 轉成時間戳
    print(time_stamp)

    return time_stamp

if __name__ =="__main__":
    df = anue_GET_NEWS_time("202101310830", "202101301330")

'''
import time
1610985600&endAt=1611935999 1/19 - 1/29

1610726400 & endAt = 1611676799 & limit = 30
time.struct_time(tm_year=2021, tm_mon=1, tm_mday=16, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=5, tm_yday=16, tm_isdst=0)
time.struct_time(tm_year=2021, tm_mon=1, tm_mday=26, tm_hour=23, tm_min=59, tm_sec=59, tm_wday=1, tm_yday=26, tm_isdst=0)

1610640000 to 1611590399
time.struct_time(tm_year=2021, tm_mon=4, tm_mday=7, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=4, tm_yday=15, tm_isdst=0)
time.struct_time(tm_year=2021, tm_mon=4, tm_mday=8, tm_hour=23, tm_min=59, tm_sec=59, tm_wday=0, tm_yday=25, tm_isdst=0)

1611590399-1610640000
datetime.datetime.fromtimestamp(1611935999) #datetime.datetime(2021, 1, 25, 23, 59, 59)
dt = datetime.datetime.today() - datetime.datetime.fromtimestamp(1611763199) # 1/27
dta = (dt.days + 1)*86400 + 1611763199
dtb = dta - 11*86400 +1



'''