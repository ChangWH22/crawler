import pandas as pd
from bs4 import BeautifulSoup
import crawler.tool as crawler_tool
import datetime
import time
import random
import re

def rti_GET_NEWS_time(decide_time_begin, decide_time_end):
    begin_time = datetime.datetime.today()
    title = []
    publish_time = []
    section = []
    body = []
    source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")
    loop_flag = False

    for page in range(1, 100):
        print("start collecting page {page}".format(page=page))
        home_url = "https://www.rti.org.tw/news/list/categoryId/2/page/" + str(page)
        r = crawler_tool.url_retry(home_url)
        soup = BeautifulSoup(r, "lxml")

        time.sleep(5)

        for i in range(len(soup.select("div.main_wrapper ul a"))):
            content_url = "https://www.rti.org.tw"+soup.select("div.main_wrapper ul a")[i]["href"]
            r2 = crawler_tool.url_retry(content_url)
            soup2 = BeautifulSoup(r2, "lxml")
            r_time = datetime.datetime.strptime(
                re.sub("[^0-9]", "", soup2.find("li", attrs={"class": "date"}).string),"%Y%m%d%H%M")

            if r_time > b_time:
                continue

            elif r_time < e_time:
                loop_flag = True
                print("Web Crawler has collected Rti data from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                break

            else:
                section.append("財經")
                title.append(soup2.find("title").string.split("-")[0])
                source.append(soup2.find("title").string.split("-")[-1])
                publish_time.append(r_time)
                body.append(crawler_tool.clean_html("".join(str(x) for x in soup2.select("article p"))))
                print(r_time)
                time.sleep(random.uniform(0,2))

        if loop_flag:
            break

    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body})
    file_name = "D:/User/Desktop/corpus/news/temporarily/" + decide_time_begin + "_" + decide_time_end + "_rti.csv"
    df.to_csv(file_name, encoding="utf-8")
    print("processing time:", datetime.datetime.today() - begin_time)

    return df

def rti_GET_NEWS_time_threading(decide_time_begin, decide_time_end,q):
    title = []
    publish_time = []
    section = []
    body = []
    source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    loop_flag = False

    for page in range(1, 100):
        print("start collecting Rti page {page}".format(page=page))
        home_url = "https://www.rti.org.tw/news/list/categoryId/2/page/" + str(page)
        r = crawler_tool.url_retry(home_url)
        soup = BeautifulSoup(r, "lxml")

        time.sleep(5)

        for i in range(len(soup.select("div.main_wrapper ul a"))):
            content_url = "https://www.rti.org.tw" + soup.select("div.main_wrapper ul a")[i]["href"]
            r2 = crawler_tool.url_retry(content_url)
            soup2 = BeautifulSoup(r2, "lxml")
            r_time = datetime.datetime.strptime(
                re.sub("[^0-9]", "", soup2.find("li", attrs={"class": "date"}).string), "%Y%m%d%H%M")

            if r_time > b_time:
                continue

            elif r_time < e_time:
                loop_flag = True
                print(
                    "Web Crawler has collected Rti data from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                break

            else:
                section.append("財經")
                title.append(re.sub(r"\s{1,}","",soup2.find("title").string.split("-")[0]))
                source.append(soup2.find("title").string.split("-")[-1])
                publish_time.append(r_time)
                body.append(crawler_tool.clean_html("".join(str(x) for x in soup2.select("article p"))))
                print("Rti:", r_time)
                time.sleep(random.uniform(0, 2))

        if loop_flag:
            break

    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body})
    file_name = "D:/User/Desktop/corpus/news/rti/" + decide_time_begin + "_" + decide_time_end + "_rti.csv"
    df.to_csv(file_name, encoding="utf-8")
    q.put(df)



