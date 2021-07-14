import requests as rq
import pandas as pd
import re
import os
import time
import sys
import pyodbc
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


df = pd.DataFrame(columns= columns)

Options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
webdriver_path = 'D:/User/Desktop/chromedriver.exe'
options = Options()
driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
driver.get('https://ndltd.ncl.edu.tw/')
driver.find_element_by_xpath('//a[@title="指令查詢"]').click()
driver.find_element_by_id('ysearchinput0').send_keys('"文字探勘".ti,kw')
driver.find_element_by_id('gs32search').click()
cookie = re.findall(r'ccd=(.*?)/', driver.current_url)[0] # cookie每次登入都會改變或是爬一定數量就會改變

r1 = 1
while r1 <= 1000:
    time.sleep(1)
    columns = []
    values = []
    try:
        driver.get('https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd={}/record?r1={}&h1=0'.format(cookie, r1))
        soup = BeautifulSoup(driver.page_source)
        soup.find('meta', attrs={'name':'description'})
        for i in soup.find('table', {'id': 'format0_disparea'}).findAll('tr'):
            if 'std1' in str(i):
                #                 print(i.find('th',{'class':'std1'}).text)
                columns.append(i.find('th', {'class': 'std1'}).text)
                #                 print(i.find('td',{'class':'std2'}).text)
                values.append(i.find('td', {'class': 'std2'}).text)

        # 永久網址
        columns.append('永久網址')
        try:
            permanent = soup.find('input', {'id': 'fe_text1'})['value']
        except:
            permanent = ''
        values.append(permanent)

        # 摘要
        columns.append('摘要')
        try:
            abst = soup.find('td', {'class': 'stdncl2'}).text
        except:
            abst = ''
        values.append(abst)
        #         print('摘要：', abst)


        ndf = pd.DataFrame(data=values, index=columns).T

        df = df.append(ndf,ignore_index=True)
        r1 += 1
        print(r1)
    except:
        # Cookie 失效時自動重啟 Selenium 取得新的 Cookie，並更新參數
        print('Get New Cookie')
        Options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        webdriver_path = 'D:/User/Desktop/chromedriver.exe'
        options = Options()
        driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
        driver.get('https://ndltd.ncl.edu.tw/')
        driver.find_element_by_xpath('//a[@title="指令查詢"]').click()
        driver.find_element_by_id('ysearchinput0').send_keys('"文字探勘".ti,kw')
        driver.find_element_by_id('gs32search').click()
        cookie = re.findall(r'ccd=(.*?)/', driver.current_url)[0]

df = df.drop(['本論文永久網址:','研究生(外文):','論文名稱(外文):','指導教授(外文):','口試委員(外文):','口試日期:', '論文種類:',
         '論文頁數:','相關次數:','DOI:', 'IG URL:', 'Facebook:'], axis=1)
df.to_csv('D:/User/Desktop/論文_.csv')

import collections
import jieba
import numpy as np
df = pd.read_csv('D:/User/Desktop/論文.csv')
df.info()
df = df.sort_values("畢業學年度:")
df_filter = df[(df["學類:"] == '企業管理學類') | (df["學類:"] == '其他商業及管理學類')|(df["學類:"] == '財務金融學類')|(df["學類:"] == '統計學類')|
   (df["學類:"] == '會計學類')]

df = df.fillna("0")
jieba.set_dictionary('dict.txt.big')
jieba.add_word('情緒分析')
filter = []
for y in ['股票','財經','經濟','基金','金融','財報','匯率','市場']:
    filter.extend([x for x in range(df.shape[0]) if y in df.loc[x,"摘要"]])
filter_multiple = list(set(filter))

list(jieba.cut('台灣金融弊案'))
text_ = []
len_ = []
for i in filter_multiple:
    text_.extend(list(set(list(jieba.cut(df.loc[i,"摘要"],cut_all=True)))))
    len_.append(len(list(jieba.cut(df.loc[i,"摘要"],cut_all=True))))

df_tfidf = pd.DataFrame({'len':len_,'text':text_})
all_word = []
for i in filter_multiple:
    all_word.extend(list(jieba.cut(df.loc[i,"摘要"])))
all_word = list(set(all_word))
tf1 = pd.DataFrame(data=np.zeros(len(all_word)),index=all_word).T
while tf.shape[0]< df_tfidf.shape[0]:
    tf = tf.append(tf1)
tf = tf.reset_index()
for i in range(1, df_tfidf.shape[0]):
    for j, value in enumerate(df_tfidf.loc[i, 'text']):
        print(value)
        tf.loc[i,value] += 1

tfdevlen = tf.copy()
tfdevlen = tfdevlen.div(df_tfidf.loc[:,'len'],axis=0)
idf = np.log10(216 / (tf!=0).sum(axis=0))
tf_idf = tfdevlen.multiply(idf, axis=1)

tf_idf[tf_idf.columns[0]] = filter_multiple
tf_idf.to_csv('D:/User/Desktop/論文_tfidf.csv')
tf_idf = tf_idf.sort_values('level_0')
string_list = []

for j in range(tf_idf.shape[0]):
    string = ''
    for i, value in enumerate(tf_idf.iloc[j, 1:].nlargest(20).items()):
        string+=value[0]
        string+='/'
    string_list.append(string)
string_list[0]
df_tfidf_keyword = pd.DataFrame({"papernum":tf_idf.loc[:,'level_0'].values,
                                "constract":string_list})
df_tfidf_keyword.to_csv('D:/User/Desktop/論文_tfidf_keyword.csv')
# key word

key_word = []
key_word_en = []
for i in range(df_filter.shape[0]):
    try:
        key_word.extend(df_filter.loc[i,'中文關鍵詞:'].split('、'))
    except:
        pass
key_word_en.lower
key_word_en = [x.lower() for x in key_word_en]
key_word_top = collections.Counter(text_).most_common(500)
key_word_top_en = collections.Counter(key_word_en).most_common(50)
key_1 = []
key_2 = []
for i in range(len(key_word_top)):
    key_1.append(key_word_top[i][0])
    key_2.append(key_word_top[i][1])

df_1 = pd.DataFrame({"key": key_1, "value": key_2})
df_1.to_csv('D:/User/Desktop/jieba_filter.csv')