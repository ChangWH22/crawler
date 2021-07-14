import pandas as pd
import crawler.tool as crawler_tool
import requests as rq
from bs4 import BeautifulSoup
import datetime
import time
import random
import re

def chinatime_GET_NEWS_time(decide_time_begin, decide_time_end):

    begin_time = datetime.datetime.today()
    Title = []
    Publish_time = []
    Section = []
    Body = []
    Source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")
    print(b_time, "\n", e_time)
    loop_flag = False

    for page in range(1, 11):
        chinatime_home = "https://www.chinatimes.com/money/total?page=" + str(page) + "&chdtv"

        try:
            print("start conectting...%s" % page)
            r = crawler_tool.url_retry(chinatime_home)
            soup = BeautifulSoup(r, "lxml")
            time.sleep(5)

            for i in range(len(soup.select("h3.title a"))):
                chinatime_financial_url = "https://www.chinatimes.com" + soup.select("h3.title a")[i]["href"]

                try:
                    r2 = crawler_tool.url_retry(chinatime_financial_url)
                    soup2 = BeautifulSoup(r2, "lxml")
                    r_time = datetime.datetime.strptime(soup2.find("meta", attrs={"name":"pubdate"})["content"], "%Y-%m-%dT%H:%M:%S+08:00")

                    if r_time > b_time:
                        continue

                    if r_time < e_time:
                        print("Web Crawler has collected data from {b_time} to {e_time}".format(b_time= b_time, e_time= e_time))
                        loop_flag = True
                        break

                    else:
                        Publish_time.append(r_time)
                        #Publish_time.append(datetime.datetime.strptime(soup2.find("meta",attrs={"name":"pubdate"})["content"],"%Y-%m-%dT%H:%M:%S+08:00"))
                        Title.append(soup2.find("h1").string)
                        Section.append(soup2.find("meta", attrs={"name": "section"})["content"])
                        Source.append(soup2.find("meta", attrs={"name": "source"})["content"])
                        body = soup2.select("div.article-body p")
                        Body.append(crawler_tool.clean_html("".join(str(x) for x in body)))
                        time.sleep(0.2)
                        print(r_time)

                except rq.exceptions.RequestException as e:
                    print("in", e)

        except rq.exceptions.RequestException as e:
            print("home", e)

        if loop_flag:
            break

    df = pd.DataFrame({"Title": Title, "Time": Publish_time, "Section": Section,  "Source": Source, "Body": Body}).sort_values(by=["Time"])
    file_name = "D:/User/Desktop/corpus/news/temporarily/" + decide_time_begin + "_" + decide_time_end + "_chinatime.csv"
    df.to_csv(file_name, encoding="utf-8")
    print("processing time:", datetime.datetime.today() - begin_time)
    return df


def chinatime_GET_NEWS_time_threading(decide_time_begin, decide_time_end, q):
    Title = []
    Publish_time = []
    Section = []
    Body = []
    Source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")
    #print(b_time, "\n", e_time)
    loop_flag = False

    for page in range(1, 11):
        chinatime_home = "https://www.chinatimes.com/money/total?page=" + str(page) + "&chdtv"

        try:
            print("start collecting ChinaTime page..%s" % page)
            r = crawler_tool.url_retry(chinatime_home)
            soup = BeautifulSoup(r, "lxml")
            time.sleep(5)

            for i in range(len(soup.select("h3.title a"))):
                chinatime_financial_url = "https://www.chinatimes.com" + soup.select("h3.title a")[i]["href"]

                try:
                    r2 = crawler_tool.url_retry(chinatime_financial_url)
                    soup2 = BeautifulSoup(r2, "lxml")
                    r_time = datetime.datetime.strptime(soup2.find("meta", attrs={"name": "pubdate"})["content"], "%Y-%m-%dT%H:%M:%S+08:00")

                    if r_time > b_time:
                        continue

                    if r_time < e_time:
                        print("Web Crawler has collected ChinaTime data from {b_time} to {e_time}".format(b_time= b_time, e_time= e_time))
                        loop_flag = True
                        break

                    else:
                        Publish_time.append(r_time)
                        Title.append(re.sub(r"\s{1,}","",soup2.find("h1").string))
                        Section.append(soup2.find("meta", attrs={"name": "section"})["content"])
                        Source.append(soup2.find("meta", attrs={"name": "source"})["content"])
                        body = soup2.select("div.article-body p")
                        Body.append(crawler_tool.clean_html("".join(str(x) for x in body)))
                        time.sleep(random.uniform(0, 2))
                        print("ChinaTime:", r_time)

                except rq.exceptions.RequestException as e:
                    print("in", e)

        except rq.exceptions.RequestException as e:
            print("home", e)

        if loop_flag:
            break

    df = pd.DataFrame({"Title": Title, "Time": Publish_time, "Section": Section,  "Source": Source, "Body": Body}).sort_values(by=["Time"])
    file_name = "D:/User/Desktop/corpus/news/chinatime/" + decide_time_begin + "_" + decide_time_end + "_chinatime.csv"
    df.to_csv(file_name, encoding="utf-8")
    q.put(df)


