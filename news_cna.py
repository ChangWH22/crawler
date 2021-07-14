import requests as rq
from bs4 import BeautifulSoup
import json
import crawler.tool as crawler_tool
import time
import datetime
import pandas as pd
import random
import re


def cna_GET_NEWS_time_threading(decide_time_begin, decide_time_end, q):

    title = []
    publish_time = []
    body = []
    section = []
    source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    for category in ["aie", "asc"]:

        loop_flag = False

        for pageidx in range(1, 6):
            resp = rq.post("https://www.cna.com.tw/cna2018api/api/WNewsList", {"action": "0",
                                                                               "category": category,
                                                                               "pageidx": pageidx,
                                                                               "pagesize": "20"})

            j = json.loads(resp.content)
            for i in range(len(j['ResultData']["Items"])):
                r_time = datetime.datetime.strptime(j['ResultData']["Items"][i]["CreateTime"], "%Y/%m/%d %H:%M")

                if r_time > b_time:
                    continue

                elif r_time < e_time:
                    loop_flag = True
                    print("Web Crawler has collected 中央通訊社  from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                    break

                else:
                    url = j['ResultData']["Items"][i]["PageUrl"]
                    section.append(j['ResultData']["Items"][i]["ClassName"])
                    title.append(re.sub(r"\s{1, }", "", j['ResultData']["Items"][i]["HeadLine"]))
                    publish_time.append(r_time)
                    soup = BeautifulSoup(rq.get(url).text, "lxml")
                    source.append("中央通訊社")
                    body.append("".join(crawler_tool.clean_html(str(x)) for x in soup.select("div.paragraph p")))
                    print("中央通訊社:", category, r_time)
                    time.sleep(random.uniform(0.5, 1.5))
            if loop_flag == True:
                break

    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body})
    file_name = "D:/User/Desktop/corpus/news/cna/" + decide_time_begin + "_" + decide_time_end + "_cna.csv"
    df.to_csv(file_name, encoding="utf-8")
    q.put(df)

def cna_GET_NEWS_time(decide_time_begin, decide_time_end):

    title = []
    publish_time = []
    body = []
    section = []
    source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    for category in ["aie", "asc"]:

        loop_flag = False

        for pageidx in range(1, 6):
            resp = rq.post("https://www.cna.com.tw/cna2018api/api/WNewsList", {"action": "0",
                                                                               "category": category,
                                                                               "pageidx": pageidx,
                                                                               "pagesize": "20"})

            j = json.loads(resp.content)
            for i in range(len(j['ResultData']["Items"])):
                r_time = datetime.datetime.strptime(j['ResultData']["Items"][i]["CreateTime"], "%Y/%m/%d %H:%M")

                if r_time > b_time:
                    continue

                elif r_time < e_time:
                    loop_flag = True
                    print("Web Crawler has collected 中央通訊社  from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                    break

                else:
                    url = j['ResultData']["Items"][i]["PageUrl"]
                    section.append(j['ResultData']["Items"][i]["ClassName"])
                    title.append(re.sub(r"\s{1, }", "", j['ResultData']["Items"][i]["HeadLine"]))
                    publish_time.append(r_time)
                    soup = BeautifulSoup(rq.get(url).text, "lxml")
                    source.append("中央通訊社")
                    body.append("".join(crawler_tool.clean_html(str(x)) for x in soup.select("div.paragraph p")))
                    print("中央通訊社:", category, r_time)
                    time.sleep(random.uniform(0.5, 1.5))
            if loop_flag == True:
                break

    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body})
    file_name = "D:/User/Desktop/corpus/news/temporarily/" + decide_time_begin + "_" + decide_time_end + "_cna.csv"
    df.to_csv(file_name, encoding="utf-8")




