from bs4 import BeautifulSoup
import crawler.tool as crawler_tool
import re
import datetime
import pandas as pd
import time
import random


def moneyDJ_GET_NEWS_time_threading(decide_time_begin, decide_time_end, q):
    title = []
    publish_time = []
    body = []
    section = []
    source = []

    loop_flag = False
    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    for page in range(1, 50):
        home_url = "https://www.moneydj.com/KMDJ/News/NewsRealList.aspx?index1="+str(page)+"&a=MB06"
        r = crawler_tool.url_retry(home_url)
        soup = BeautifulSoup(r, "lxml")
        print("start collecting moneyDJ page..%s" % page)
        for i in range(len(soup.find("table",attrs={"class": "forumgrid"}).find_all("a"))):
            url = "https://www.moneydj.com"+soup.find("table",attrs={"class": "forumgrid"}).find_all("a")[i]["href"]
            r2 = crawler_tool.url_retry(url)
            soup2 = BeautifulSoup(r2, "lxml")
            maindata = soup2.select("article#MainContent_Contents_mainArticle")[0]

            r_time = datetime.datetime.strptime(soup2.find('span', attrs={'id': 'MainContent_Contents_lbDate'}).text,
                                                "%Y/%m/%d %H:%M")

            if r_time > b_time:
                continue

            elif r_time < e_time:
                print("Web Crawler has collected moneyDJ  from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                loop_flag = True
                break

            else:
                title_temp = re.sub(r"\s{1, }", "", soup2.select("h1 span")[0].string)
                body_temp = re.sub(r"\s{1, }", "", crawler_tool.clean_html(str(maindata)))

                if len(re.sub(r"[0-9.]", "", body_temp)) / len(body_temp) < 0.5:
                    title.append(title_temp)
                    body.append(title_temp)
                elif len(title_temp)+100 > len(re.sub(r"[a-zA-Z0-9/,=?:;.{}()#%'&-]", "", body_temp)):
                    title.append(title_temp)
                    body.append(title_temp)
                else:
                    title.append(title_temp)
                    body.append(body_temp)

                publish_time.append(r_time)
                section.append("台股")
                source.append("moneyDJ")
                print("moneyDJ:", r_time)
                time.sleep(random.uniform(0, 1.5))

        if loop_flag:
            break
    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body})
    file_name = "D:/User/Desktop/corpus/news/moneyDJ/" + decide_time_begin + "_" + decide_time_end + "_moneyDJ.csv"
    df.to_csv(file_name, encoding="utf-8")
    q.put(df)


def moneyDJ_GET_NEWS_time(decide_time_begin, decide_time_end):
    title = []
    publish_time = []
    body = []
    section = []
    source = []

    loop_flag = False

    b_time = datetime.datetime.strptime(decide_time_begin, "%Y%m%d%H%M")
    e_time = datetime.datetime.strptime(decide_time_end, "%Y%m%d%H%M")

    for page in range(1, 50):
        home_url = "https://www.moneydj.com/KMDJ/News/NewsRealList.aspx?index1="+str(page)+"&a=MB06"
        r = crawler_tool.url_retry(home_url)
        soup = BeautifulSoup(r, "lxml")
        print("start collecting moneyDJ page..%s" % page)
        for i in range(len(soup.find("table",attrs={"class": "forumgrid"}).find_all("a"))):

            url = "https://www.moneydj.com"+soup.find("table",attrs={"class": "forumgrid"}).find_all("a")[i]["href"]
            r2 = crawler_tool.url_retry(url)
            soup2 = BeautifulSoup(r2, "lxml")
            maindata = soup2.select("article#MainContent_Contents_mainArticle")[0]

            r_time = datetime.datetime.strptime(soup2.find('span',attrs={'id':'MainContent_Contents_lbDate'}).text,
                                                "%Y/%m/%d %H:%M")

            if r_time > b_time:
                continue

            elif r_time < e_time:
                print("Web Crawler has collected moneyDJ  from {b_time} to {e_time}".format(b_time=b_time, e_time=e_time))
                loop_flag = True
                break

            else:
                title_temp = re.sub(r"\s{1, }", "", soup2.select("h1 span")[0].string)
                body_temp = re.sub(r"\s{1, }", "", crawler_tool.clean_html(str(maindata)))

                if len(re.sub(r"[0-9.]", "", body_temp)) / len(body_temp) < 0.5:
                    title.append(title_temp)
                    body.append(title_temp)
                elif len(title_temp)+100 > len(re.sub(r"[a-zA-Z0-9/,=?:;.{}()#%'&-]", "", body_temp)):
                    title.append(title_temp)
                    body.append(title_temp)
                else:
                    title.append(title_temp)
                    body.append(body_temp)

                publish_time.append(r_time)
                section.append("台股")
                source.append("moneyDJ")
                print("moneyDJ:", r_time)
                time.sleep(random.uniform(0.5, 1.5))

        if loop_flag:
            break
    df = pd.DataFrame({"Title": title, "Time": publish_time, "Section": section, "Source": source, "Body": body})
    file_name = "D:/User/Desktop/corpus/news/temporarily/" + decide_time_begin + "_" + decide_time_end + "_moneyDJ.csv"
    df.to_csv(file_name, encoding="utf-8")


