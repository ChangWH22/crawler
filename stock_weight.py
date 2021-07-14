import requests as rq
from bs4 import BeautifulSoup
import re
import pandas as pd


def clean_data(string):
    string = re.sub(r'[\n\r\t]', '', string)
    string = re.sub(r'\s{1,}', '', string)
    string = re.sub(r'%', '', string)
    return string


r = rq.get('https://www.taifex.com.tw/cht/9/futuresQADetail')

soup = BeautifulSoup(r.text, 'lxml')
num = []; name = []; weight = []
for i in range(1, len(soup.find_all('tr'))):
    num.append(clean_data(soup.find_all('tr')[i].find_all('td')[1].text))
    name.append(clean_data(soup.find_all('tr')[i].find_all('td')[2].text))
    weight.append(clean_data(soup.find_all('tr')[i].find_all('td')[3].text))
    num.append(clean_data(soup.find_all('tr')[i].find_all('td')[5].text))
    name.append(clean_data(soup.find_all('tr')[i].find_all('td')[6].text))
    weight.append(clean_data(soup.find_all('tr')[i].find_all('td')[7].text))

df = pd.DataFrame({'num': num, 'name': name, 'weight': weight})
df.to_csv('D:/User/Desktop/情緒分析/stock_weight.csv')