from bs4 import BeautifulSoup
import crawler.tool as crawler_tool
import json
import re
import datetime
import pandas as pd
import time
import random


def tvbs_GET_NEWS_time_threading(decide_time_begin, decide_time_end, q):
    title = []
    publish_time = []
    body = []
    section = []
    source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    r = crawler_tool.url_retry("https://news.tvbs.com.tw/money")
    soup = BeautifulSoup(r, "lxml")

    for i in range(len(soup.select("div.content_center_contxt_box_news a"))):
        url = "https://news.tvbs.com.tw"+soup.select("div.content_center_contxt_box_news a")[i]["href"]
        r2 = crawler_tool.url_retry(url)
        soup2 = BeautifulSoup(r2, "lxml")
        try:
            j = json.loads(soup2.find("script", attrs={"type": "application/ld+json"}).string)
            r_time = datetime.datetime.strptime(j["datePublished"], "%Y/%m/%d %H:%M")

            if r_time > b_time:
                continue

            elif r_time < e_time:
                print("Web Crawler has collected TVBS  from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                break

            else:
                title.append(re.sub(r"\s{1, }", "", j["headline"].split("│")[0]))
                publish_time.append(r_time)
                body.append(j["articleBody"])
                section.append(j["articleSection"])
                source.append("TVBS新聞網")
                print("TVBS新聞網:",  r_time)

                time.sleep(random.uniform(0.5, 1.5))
        except json.decoder.JSONDecodeError:
            print("json.decoder.JSONDecodeError")
    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body})
    file_name = "D:/User/Desktop/corpus/news/tvbs/" + decide_time_begin + "_" + decide_time_end + "_tvbs.csv"
    df.to_csv(file_name, encoding="utf-8")
    q.put(df)



def tvbs_GET_NEWS_time(decide_time_begin, decide_time_end):
    title = []
    publish_time = []
    body = []
    section = []
    source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    r = crawler_tool.url_retry("https://news.tvbs.com.tw/money")
    soup = BeautifulSoup(r, "lxml")

    for i in range(len(soup.select("div.content_center_contxt_box_news a"))):
        url = "https://news.tvbs.com.tw"+soup.select("div.content_center_contxt_box_news a")[i]["href"]
        r2 = crawler_tool.url_retry(url)
        soup2 = BeautifulSoup(r2, "lxml")
        try:
            j = json.loads(soup2.find("script", attrs={"type": "application/ld+json"}).string)
            r_time = datetime.datetime.strptime(j["datePublished"], "%Y/%m/%d %H:%M")

            if r_time > b_time:
                continue

            elif r_time < e_time:
                print("Web Crawler has collected TVBS  from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                break

            else:
                title.append(re.sub(r"\s{1, }", "", j["headline"].split("│")[0]))
                publish_time.append(r_time)
                body.append(j["articleBody"])
                section.append(j["articleSection"])
                source.append("TVBS新聞網")
                print("TVBS新聞網:",  r_time)

                time.sleep(random.uniform(0.5, 1.5))
        except json.decoder.JSONDecodeError:
            print("json.decoder.JSONDecodeError")
    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body})
    file_name = "D:/User/Desktop/corpus/news/temporarily/" + decide_time_begin + "_" + decide_time_end + "_tvbs.csv"
    df.to_csv(file_name, encoding="utf-8")


if __name__ == "__main__":
    tvbs_GET_NEWS_time("202101040830", "202012311330")

