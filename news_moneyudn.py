import pandas as pd
import time
import datetime
import crawler.tool as crawler_tool
import requests as rq
from bs4 import BeautifulSoup
import random
import re


def moneyudn_GET_NEWS_time_threading(decide_time_begin, decide_time_end, q):

    title = []
    publish_time = []
    section = []
    body = []
    source = []

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    loop_flag = False

    for page in range(1, 30):
        print("start collecting 經濟日報(moneyudn) page {page}".format(page=page))
        home_url = "https://money.udn.com/rank/newest/1001/0/" + str(page)
        time.sleep(2)
        try:
            r = crawler_tool.url_retry(home_url)
            soup = BeautifulSoup(r, "lxml")

            for i in range(len(soup.select("td a"))):
                url2 = soup.select("td a")[i]["href"]
                try:
                    html_page = crawler_tool.url_retry(url2)
                    soup2 = BeautifulSoup(html_page, "lxml")
                    r_time = datetime.datetime.strptime(soup2.find("meta", attrs={"name": "date"})["content"],
                                                        "%Y/%m/%d %H:%M:%S")
                    if r_time > b_time:
                        continue

                    if r_time < e_time:
                        loop_flag = True
                        print("Web Crawler has collected money_udn data from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                        break

                    else:
                        sub_section = soup2.select("div#nav a")[1].string
                        if sub_section == "品味" or sub_section == "會員專區" or sub_section == "兩岸":
                            time.sleep(random.uniform(0, 1.5))
                            continue
                        else:
                            body.append(crawler_tool.clean_html("".join(str(x) for x in soup2.select("div#article_body p "))))
                            publish_time.append(r_time)  # time
                            title.append(re.sub(r"\s{1, }", "", soup2.find("meta", attrs={"property": "og:title"})["content"].split("|")[0]))
                            section.append(sub_section)
                            source.append(soup2.select("div#nav a")[0].string)

                            time.sleep(random.uniform(0, 1.5))
                            print("moneyudn:", r_time)
                except rq.exceptions.RequestException as e:
                    print("in", e)
        except rq.exceptions.RequestException as e2:
            print("home", e2)

        if loop_flag:
            break

    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body}).sort_values(by=["Time"])
    file_name = "D:/User/Desktop/corpus/news/money_udn/" + decide_time_begin + "_" + decide_time_end + "_moneyudn.csv"
    df.to_csv(file_name, encoding="utf-8")
    q.put(df)


def moneyudn_GET_NEWS_time(decide_time_begin, decide_time_end):
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
        home_url = "https://money.udn.com/rank/newest/1001/0/" + str(page)
        time.sleep(3)
        try:
            r = crawler_tool.url_retry(home_url)
            soup = BeautifulSoup(r, "lxml")

            for i in range(len(soup.select("td a"))):
                url2 = soup.select("td a")[i]["href"]

                html_page = crawler_tool.url_retry(url2)
                soup2 = BeautifulSoup(html_page, "lxml")
                r_time = datetime.datetime.strptime(soup2.find("meta", attrs={"name": "date"})["content"],
                                                    "%Y/%m/%d %H:%M:%S")
                if r_time > b_time:
                    continue

                elif r_time < e_time:
                    loop_flag = True
                    print("Web Crawler has collected money_udn data from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                    break

                else:
                    sub_section = soup2.select("div#nav a")[-1].string
                    if sub_section == "品味" or sub_section == "會員專區" or sub_section == "兩岸":
                        time.sleep(random.randint(1, 5))
                        continue
                    else:
                        print(r_time)
                        body.append(crawler_tool.clean_html("".join(str(x) for x in soup2.select("div#article_body p "))))
                        publish_time.append(r_time)  # time
                        title.append(re.sub(r"\s{1, }", "", soup2.find("meta", attrs={"property": "og:title"})["content"].split("|")[0]))
                        section.append(sub_section)
                        source.append(soup2.select("div#nav a")[0].string)

                        time.sleep(0.2)
        except rq.exceptions.RequestException as e2:
            print("home", e2)

        if loop_flag:
            break

    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body}).sort_values(by=["Time"])
    file_name = "D:/User/Desktop/corpus/news/temporarily/" + decide_time_begin + "_" + decide_time_end + "_moneyudn.csv"
    df.to_csv(file_name, encoding="utf-8")
    print("processing time:", datetime.datetime.today() - begin_time)
    return df




