from queue import Queue
import threading
import datetime
import pyodbc
from sqlalchemy import create_engine
import requests as rq
import pandas as pd
from bs4 import BeautifulSoup
import crawler.tool as crawler_tool
import time
import random
import os
import json
import re

from crawler.ctee import ctee_GET_NEWS_time_threading
from crawler.anue import anue_GET_NEWS_time_threading
from crawler.rti import rti_GET_NEWS_time_threading
from crawler.money_udn import moneyudn_GET_NEWS_time_threading
from crawler.China_Time import chinatime_GET_NEWS_time_threading
from crawler.setn import setn_GET_NEWS_time_threading
from crawler.cna import cna_GET_NEWS_time_threading
from crawler.tvbs import tvbs_GET_NEWS_time_threading
from crawler.moneyDJ import moneyDJ_GET_NEWS_time_threading


def get_data(decide_time_begin, decide_time_end):
    begin_time = datetime.datetime.today()
    q = Queue()
    threads = []

    for kind in [ctee_GET_NEWS_time_threading, moneyudn_GET_NEWS_time_threading, chinatime_GET_NEWS_time_threading,
                 setn_GET_NEWS_time_threading, anue_GET_NEWS_time_threading, rti_GET_NEWS_time_threading,
                 cna_GET_NEWS_time_threading, tvbs_GET_NEWS_time_threading, moneyDJ_GET_NEWS_time_threading]:
        t = threading.Thread(target=kind, args=(decide_time_begin, decide_time_end, q))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

    result = []
    for _q in range(len(threads)):
        result.append(q.get())

    df = pd.concat([result[i] for i in range(len(result))], ignore_index=True)
    df = df.drop_duplicates(subset=["Title"]).sort_values("Time")
    file_name = "D:/User/Desktop/corpus/news/_concat/" + decide_time_begin + "_" + decide_time_end + "_concat.csv"
    df.to_csv(file_name, encoding="utf-8")
    print("processing time:", datetime.datetime.today() - begin_time)
    return df


def creator():
    # connect database of sentiment index
    return pyodbc.connect(r'Driver={SQL Server};Server=DESKTOP-OKF0JOA;Database=test;Trusted_Connection=yes')


if __name__ == "__main__":
    today = datetime.datetime.today()

    if today.month < 10:
        today_month = "0" + str(today.month)
    else:
        today_month = str(today.month)

    if today.day < 10:
        today_day = '0' + str(today.day)
    else:
        today_day = str(today.day)

    # 盤中新聞
    if today.hour >= 14:
        time_begin = str(today.year) + today_month + today_day + "1330"
        time_end = str(today.year) + today_month + today_day + "0830"

    # 盤後新聞 1330-0830
    elif 8 <= today.hour < 14:
        yesterday = today - datetime.timedelta(days=1)

        if yesterday.month < 10:
            yesterday_month = "0" + str(yesterday.month)
        else:
            yesterday_month = str(yesterday.month)

        if yesterday.day < 10:
            yesterday_day = '0' + str(yesterday.day)
        else:
            yesterday_day = str(yesterday.day)

        time_begin = str(today.year) + today_month + today_day + "0830"
        time_end = str(yesterday.year) + yesterday_month + yesterday_day + "1330"

    print("begin time:", time_begin)
    print("end time:  ", time_end)
    df_news = get_data(time_begin, time_end)
    df_news = df_news.reset_index(drop=True)
    Engine = create_engine('mssql://', creator=creator)
    cnx = Engine.connect()
    df_news.to_sql("NEWS", cnx, index=False, if_exists="append", chunksize=10000)

'''
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=DESKTOP-OKF0JOA;DATABASE=test')
    cursor = conn.cursor()
    for i in range(0, len(df)):
        try:
            if pd.isnull(df["Body"][i]):
                print("null")
            else:
                cursor.execute("insert into NEWS (Title,Time,Section,Source,Body) values(?,?,?,?,?)",
                               df["Title"][i], df["Time"][i], df["Section"][i],
                               df["Source"][i], df["Body"][i])
        except pyodbc.DataError:
            print(i)

    cursor.commit()
'''
