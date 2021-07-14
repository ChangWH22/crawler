import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
import crawler.tool as crawler_tool
import datetime
import time
import random
import re


def setn_GET_NEWS_time(decide_time_begin, decide_time_end):
    begin_time = datetime.datetime.today()
    Title = []
    Publish_time = []
    Section = []
    Body = []
    Source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")
    loop_flag = False

    for page in range(1, 19):

        print("start collecting page {page}".format(page=page))
        home_url = "https://www.setn.com/ViewAll.aspx?PageGroupID=2&p=" + str(page)
        time.sleep(5)

        try:
            r = crawler_tool.url_retry(home_url)
            soup = BeautifulSoup(r, "lxml")

            for i in range(len(soup.select("h3.view-li-title a"))):
                content_url = ("https://www.setn.com/" + soup.select("h3.view-li-title a")[i]["href"])
                r2 = crawler_tool.url_retry(content_url)
                soup2 = BeautifulSoup(r2, "lxml")

                r_time = datetime.datetime.strptime(soup2.find("meta",attrs={"name":"pubdate"})["content"]
                                                    ,"%Y-%m-%dT%H:%M:%S")

                if r_time > b_time:
                    continue

                elif r_time < e_time:
                    loop_flag = True
                    print(
                        "Web Crawler has collected setn data from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                    break

                else:
                    Section.append(soup2.find("meta",attrs={"property":"og:title"})["content"].split("|")[1])
                    Title.append(soup2.find("meta",attrs={"property":"og:title"})["content"].split("|")[0])
                    Source.append(soup2.find("meta",attrs={"property":"og:title"})["content"].split("|")[2])
                    Publish_time.append(r_time)
                    Body.append(crawler_tool.clean_html("".join(str(x) for x in soup2.select("div#Content1 p"))))
                    print(r_time)
                    time.sleep(0.2)

        except rq.exceptions.RequestException as e2:
            print("home", e2)

        if loop_flag:
            break

    df = pd.DataFrame({"Title": Title, "Time": Publish_time, "Section": Section, "Source": Source, "Body": Body})
    file_name = "D:/User/Desktop/corpus/news/temporarily/" + decide_time_begin + "_" + decide_time_end + "_setn.csv"
    df.to_csv(file_name, encoding="utf-8")
    print("processing time:", datetime.datetime.today() - begin_time)

    return df


def setn_GET_NEWS_time_threading(decide_time_begin, decide_time_end, q):
    Title = []
    Publish_time = []
    Section = []
    Body = []
    Source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")
    #print(b_time, "\n", e_time)

    loop_flag = False

    for page in range(1, 19):

        print("start collecting Setn page {page}".format(page=page))
        home_url = "https://www.setn.com/ViewAll.aspx?PageGroupID=2&p=" + str(page)
        time.sleep(5)

        try:
            r = crawler_tool.url_retry(home_url)
            soup = BeautifulSoup(r, "lxml")

            for i in range(len(soup.select("h3.view-li-title a"))):
                content_url = ("https://www.setn.com/" + soup.select("h3.view-li-title a")[i]["href"])
                r2 = crawler_tool.url_retry(content_url)
                soup2 = BeautifulSoup(r2, "lxml")

                r_time = datetime.datetime.strptime(soup2.find("meta", attrs={"name": "pubdate"})["content"]
                                                    , "%Y-%m-%dT%H:%M:%S")

                if r_time > b_time:
                    continue

                elif r_time < e_time:
                    loop_flag = True
                    print(
                        "Web Crawler has collected Setn data from {b_time} to {e_time}".format(b_time=b_time,
                                                                                          e_time=e_time))
                    break

                else:
                    Section.append(soup2.find("meta", attrs={"property": "og:title"})["content"].split("|")[1])
                    Title.append(re.sub(r"\s{1,}","",soup2.find("meta", attrs={"property": "og:title"})["content"].split("|")[0]))
                    Source.append(soup2.find("meta", attrs={"property": "og:title"})["content"].split("|")[2])
                    Publish_time.append(r_time)
                    Body.append(crawler_tool.clean_html("".join(str(x) for x in soup2.select("div#Content1 p"))))
                    print("Setn:", r_time)
                    time.sleep(random.uniform(0, 2))

        except rq.exceptions.RequestException as e2:
            print("home", e2)

        if loop_flag:
            break

    df = pd.DataFrame({"Title": Title, "Time": Publish_time, "Section": Section, "Source": Source, "Body": Body})
    file_name = "D:/User/Desktop/corpus/news/setn/" + decide_time_begin + "_" + decide_time_end + "_setn.csv"
    df.to_csv(file_name, encoding="utf-8")
    q.put(df)

