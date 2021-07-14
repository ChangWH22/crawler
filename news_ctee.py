import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
import crawler.tool as crawler_tool
import datetime
import time
import random


def ctee_GET_NEWS_time(decide_time_begin, decide_time_end):

    begin_time = datetime.datetime.today()
    Title = []
    Publish_time = []
    Section = []
    Body = []
    Source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    loop_flag = False

    for page in range(1, 11):

        print("start collecting ctee page {page}".format(page=page))
        home_url = "https://ctee.com.tw/livenews/all/page/" + str(page)
        time.sleep(5)

        try:
            r = crawler_tool.url_retry(home_url)
            soup = BeautifulSoup(r, "lxml")

            for i in range(len(soup.select("p.now-title "))):
                content_url = soup.select("p.now-title ")[i].find_all("a")[-1]["href"]
                section = soup.select("p.now-title ")[i].find("span").string
                r_time = datetime.datetime.strptime(str(b_time.year) + "/" + crawler_tool.clean_html(
                    str(soup.select("p.now-title ")[i].find_all("a")[1]).split("|")[-1]), "%Y/ %m/%d %H:%M ")

                if r_time > b_time:
                    continue

                elif r_time < e_time:
                    loop_flag = True
                    print("collected ctee news from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                    break

                else:
                    r2 = crawler_tool.url_retry(content_url)
                    soup2 = BeautifulSoup(r2, "lxml")

                    if section == "生活" or section == "政治":
                        time.sleep(random.randint(1, 3))
                        continue

                    else:
                        Title.append(soup2.select("span.post-title")[0].string)
                        Section.append(section)
                        Source.append("工商時報")
                        Publish_time.append(r_time)
                        Body.append(crawler_tool.clean_html("".join(str(x) for x in soup2.select("div.entry-content p"))))
                        print("工商時報 : ",r_time)
                        time.sleep(0.2)

        except rq.exceptions.RequestException as e2:
            print("home", e2)

        if loop_flag:
            break

    df = pd.DataFrame({"Title": Title, "Time": Publish_time, "Section": Section, "Source": Source, "Body": Body}).sort_values(by=["Time"])
    file_name = "D:/User/Desktop/corpus/news/temporarily/" + decide_time_begin + "_" + decide_time_end + "_ctee.csv"
    df.to_csv(file_name, encoding="utf-8")
    print("processing time:", datetime.datetime.today() - begin_time)
    return df


def ctee_GET_NEWS_time_threading(decide_time_begin, decide_time_end, q):

    Title = []
    Publish_time = []
    Section = []
    Body = []
    Source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    loop_flag = False

    for page in range(1,11):

        print("start ctee collecting page {page}".format(page=page))
        home_url = "https://m.ctee.com.tw/livenews/all/page/" + str(page)
        time.sleep(5)

        try:
            r = crawler_tool.url_retry(home_url)
            soup = BeautifulSoup(r, "lxml")

            for i in range(len(soup.select("p.now-title "))):
                content_url = soup.select("p.now-title ")[i].find_all("a")[-1]["href"]
                section = soup.select("p.now-title ")[i].find("span").string
                r_time = datetime.datetime.strptime(str(b_time.year) + "/" + crawler_tool.clean_html(
                    str(soup.select("p.now-title ")[i].find_all("a")[1]).split("|")[-1]), "%Y/ %m/%d %H:%M ")

                if r_time > b_time:
                    continue
                elif r_time < e_time:
                    loop_flag = True
                    print("collected ctee news from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                    break
                else:
                    r2 = crawler_tool.url_retry(content_url)
                    soup2 = BeautifulSoup(r2,"lxml")

                    if section == "生活" or section == "政治":
                        time.sleep(random.uniform(0, 1.5))
                        continue

                    else:
                        Title.append(soup2.select("span.post-title")[0].string)
                        Section.append(section)
                        Source.append("工商時報")
                        Publish_time.append(r_time)
                        Body.append(crawler_tool.clean_html("".join(str(x) for x in soup2.select("div.entry-content p"))))
                        print("ctee:", r_time)
                        time.sleep(random.uniform(0, 1.5))

        except rq.exceptions.RequestException as e2:
            print("home", e2)

        if loop_flag:
            break

    df = pd.DataFrame({"Title": Title, "Time": Publish_time, "Section": Section, "Source": Source, "Body": Body}).sort_values(by=["Time"])
    file_name = "D:/User/Desktop/corpus/news/ctee/" + decide_time_begin + "_" + decide_time_end + "_ctee.csv"
    df.to_csv(file_name, encoding="utf-8")
    q.put(df)

