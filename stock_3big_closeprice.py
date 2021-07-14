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


def creator():
    return pyodbc.connect(r'Driver={SQL Server};Server=DESKTOP-OKF0JOA;Database=stock_information;Trusted_Connection=yes;')


Engine = create_engine('mssql://', creator=creator)
cnx = Engine.connect()


def get_stock_pv(month, day):
    # 上市
    r = rq.get("https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=2021"+month+day+"&type=ALLBUT0999")
    r.encoding = "CP950"
    rt = r.text

    date_check = "110年" + month + "月" + day + "日"

    if date_check not in rt.split(",,,,,")[0].split("\r\n")[0]:
        print("輸入時間: ", date_check, "  檔案時間: ", rt.split(",,,,,")[0].split("\r\n")[0])
        sys.exit()

    rt1 = rt.split(",,,,,")[-1]
    rt2 = rt1.split("\r\n")
    rt2[4].split("\",\"")

    def clean_pv(file):
        file = re.sub("\"", "", file)
        file = re.sub(",", "", file)
        return file

    num = []
    name = []
    volume = []
    openv = []
    maxv = []
    minv = []
    closev = []

    for i in range(2, len(rt2)):
        if len(clean_pv(rt2[i].split("\",\"")[0])) == 4:
            num.append(clean_pv(rt2[i].split("\",\"")[0]))
            name.append(rt2[i].split("\",\"")[1])
            vol = re.sub(",", "", rt2[i].split("\",\"")[2])
            volume.append(int(vol)//1000)
            openv.append(rt2[i].split("\",\"")[5])
            maxv.append(rt2[i].split("\",\"")[6])
            minv.append(rt2[i].split("\",\"")[7])
            closev.append(rt2[i].split("\",\"")[8])

    s_e = pd.DataFrame({"代號": num, "名稱": name, "成交量": volume, "開盤價": openv, "最高價": maxv,
                       "最低價": minv, "收盤價": closev})
    # 上櫃
    step =0
    while step < 1:
        try:
            Options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
            webdriver_path = 'D:/User/Desktop/chromedriver.exe'
            options = Options()
            driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
            time.sleep(2)
            driver.get("https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw")
            time.sleep(2)
            option_select = Select(driver.find_element_by_name("sect"))
            time.sleep(0.5)
            option_select.select_by_value("EW")
            time.sleep(0.5)
            driver.find_element_by_id('input_date').send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            driver.find_element_by_id('input_date').send_keys(Keys.DELETE)
            time.sleep(0.5)
            driver.find_element_by_id('input_date').send_keys("110/"+month+"/"+day)
            time.sleep(0.5)
            driver.find_element_by_id('input_date').send_keys(Keys.ENTER)
            time.sleep(0.5)
            driver.find_element_by_id('input_date').send_keys(Keys.ENTER)
            time.sleep(0.5)
            driver.find_elements_by_class_name("btn-download")[0].click()
            time.sleep(1)
            driver.close()
            df = pd.read_csv("D:/User/Downloads/SQUOTE_EW_110"+month+day+".csv", encoding="CP950", delimiter=',', names=list(range(17)))
            step += 1
        except FileNotFoundError:
            pass

    date_check = "110/"+month + "/" + day

    if date_check not in df[df.columns[0]][2]:
        print("輸入時間: ", date_check, "  檔案時間: ", df[df.columns[0]][2])
        sys.exit()

    df = df.dropna(how="any").reset_index(drop=True)
    df.columns = list(df.loc[0])

    for i in range(len(df)):
        if len(df["代號"][i]) != 4:
            df = df.drop(i, axis=0)
        else:
            df["成交股數  "][i] = int(re.sub(",", "", df["成交股數  "][i]))//1000

    df = df.reset_index(drop=True)
    df = df.loc[0:, ["代號", "名稱", "成交股數  ", "收盤 ", "開盤 ", "最高 ", "最低"]]
    df.columns = ["代號", "名稱", "成交量", "收盤價", "開盤價", "最高價", "最低價"]

    concat = pd.concat([s_e, df], axis=0)
    concat = concat.sort_values("代號").reset_index(drop=True)
    concat.columns = ["ID", "Name", "成交量", "開盤價", "最高價", "最低價", "收盤價"]
    insert_time = "2021-" + month + "-" + day
    concat.insert(2, "Time", insert_time)

    concat.to_csv("D:/User/Desktop/corpus/stock/stock_110"+month+day+".csv", encoding="cp950")
    concat.to_sql("stock_pv", cnx, index=False, if_exists="append", chunksize=10000)

    file_dir = "D:/User/Downloads/SQUOTE_EW_110"+month+day+".csv"
    os.remove(file_dir)


def get_stock_3big(month, day):

    def clean_3big(file):
        file = re.sub("\"", "", file)
        file = re.sub(",", "", file)
        file = re.sub(r"\s{0,}", "", file)

        return file
    # 上市
    r = rq.get("https://www.twse.com.tw/fund/T86?response=csv&date=2021"+month+day+"&selectType=ALLBUT0999")
    rt = r.text.split("\r\n")
    date_check = "110年"+month+"月"+day+"日"

    if date_check not in rt[0]:
        print("輸入時間: ", date_check, "  檔案時間: ", rt[0])
        sys.exit()

    column_name = rt[1].split("\",\"")

    num = []
    name = []
    big_3_y_in = []
    big_3_t_in = []
    big_3_g_in = []

    big_3_y_out = []
    big_3_t_out = []
    big_3_g_out = []
    big_3_g_t = []

    big_3_gb_in = []
    big_3_gb_out = []
    big_3_gb_t = []
    big_3_g_all = []

    big_3_y = []
    big_3_t = []

    big_3_total = []

    for i in range(2, len(rt)):
        if len(clean_3big(rt[i].split("\",\"")[0])) == 4:
            num.append(clean_3big(rt[i].split("\",\"")[0]))
            name.append(clean_3big(rt[i].split("\",\"")[1]))
            big_3_y_in.append(clean_3big(rt[i].split("\",\"")[2]))
            big_3_y_out.append(clean_3big(rt[i].split("\",\"")[3]))
            big_3_y.append(clean_3big(rt[i].split("\",\"")[4]))

            big_3_t_in.append(clean_3big(rt[i].split("\",\"")[8]))
            big_3_t_out.append(clean_3big(rt[i].split("\",\"")[9]))
            big_3_t.append(clean_3big(rt[i].split("\",\"")[10]))

            big_3_g_all.append(clean_3big(rt[i].split("\",\"")[11]))

            big_3_g_in.append(clean_3big(rt[i].split("\",\"")[12]))
            big_3_g_out.append(clean_3big(rt[i].split("\",\"")[13]))
            big_3_g_t.append(clean_3big(rt[i].split("\",\"")[14]))

            big_3_gb_in.append(clean_3big(rt[i].split("\",\"")[15]))
            big_3_gb_out.append(clean_3big(rt[i].split("\",\"")[16]))
            big_3_gb_t.append(clean_3big(rt[i].split("\",\"")[17]))

            big_3_total.append(clean_3big(rt[i].split("\",\"")[18]))

    s_e = pd.DataFrame({"代號": num, "名稱": name, column_name[4]: big_3_y, column_name[10]: big_3_t,
                        column_name[11]: big_3_g_all, column_name[18]: big_3_total,
                        column_name[2]: big_3_y_in, column_name[3]: big_3_y_out,
                        column_name[8]: big_3_t_in, column_name[9]: big_3_t_out,
                        column_name[12]: big_3_g_in, column_name[13]: big_3_g_out,
                        column_name[14]: big_3_g_t, column_name[15]: big_3_gb_in,
                        column_name[16]: big_3_gb_out, column_name[17]: big_3_gb_t})

    # 上櫃
    step =0
    while step < 1:
        try:
            Options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
            webdriver_path = 'D:/User/Desktop/chromedriver.exe'
            options = Options()
            driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
            time.sleep(2)
            driver.get("https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge.php?l=zh-tw")
            time.sleep(1)
            option_select = Select(driver.find_element_by_name("sect"))
            time.sleep(0.5)
            option_select.select_by_value("EW")
            time.sleep(0.5)
            driver.find_element_by_id('input_date').send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            driver.find_element_by_id('input_date').send_keys(Keys.DELETE)
            time.sleep(0.5)
            driver.find_element_by_id('input_date').send_keys("110/"+month+"/"+day)
            time.sleep(0.5)
            driver.find_element_by_id('input_date').send_keys(Keys.ENTER)
            time.sleep(0.5)
            driver.find_element_by_id('input_date').send_keys(Keys.ENTER)
            time.sleep(0.5)
            driver.find_elements_by_class_name("btn-download")[0].click()
            time.sleep(1)
            driver.close()
            time.sleep(1)
            df = pd.read_csv("D:/User/Downloads/BIGD_110"+month+day+".csv", encoding="CP950", delimiter=',', names=list(range(24)))
            step += 1
        except FileNotFoundError:
            pass

    if date_check not in df[df.columns[0]][0]:
        print("輸入時間: ", date_check, "  檔案時間: ", df[df.columns[0]][0])
        sys.exit()

    df = df.dropna(how="any").reset_index(drop=True)
    df.columns = list(df.loc[0])
    df = df[["代號", '名稱', '外資及陸資(不含外資自營商)-買賣超股數', '投信-買賣超股數', '自營商-買賣超股數', '三大法人買賣超股數合計',
            '外資及陸資(不含外資自營商)-買進股數', '外資及陸資(不含外資自營商)-賣出股數', '投信-買進股數', '投信-賣出股數', '自營商(自行買賣)-買進股數',
             '自營商(自行買賣)-賣出股數', '自營商(自行買賣)-買賣超股數', '自營商(避險)-買進股數', '自營商(避險)-賣出股數', '自營商(避險)-買賣超股數']]
    df.columns = s_e.columns
    for i in range(len(df)):
        if len(df["代號"][i]) != 4:
            df = df.drop(i, axis=0)

    for i in range(2, df.shape[1]):
        df.iloc[:, i] = df.iloc[:, i].str.replace(",", "")

    s_e = s_e.append(df)
    s_e = s_e.sort_values("代號").reset_index(drop=True)
    s_e.iloc[0:, 2:] = round(s_e.iloc[0:, 2:].astype(float) / 1000 , 0).astype(int)
    s_e.columns = ['ID', 'Name', '外資買賣超', '投信買賣超', '自營商買賣超', '三大法人買賣超',
                   '外資買入', '外資賣出', '投信買入', '投信賣出','自營商買入_自行', '自營商賣出_自行', '自營商買賣超_自行',
                   '自營商買入_避險', '自營商賣出_避險', '自營商買賣超_避險']

    insert_time = "2021-" + month + "-" + day
    s_e.insert(2, "Time", insert_time)

    s_e.to_csv("D:/User/Desktop/corpus/stock/stock_110"+month+day+"_3big.csv", encoding="cp950")
    s_e.to_sql("stock_3big", cnx, index=False, if_exists="append", chunksize=10000)
    file_dir = "D:/User/Downloads/BIGD_110"+month+day+".csv"
    os.remove(file_dir)



if __name__ == '__main__':
    import datetime
    month = str(datetime.datetime.today().month)
    day = str(datetime.datetime.today().day)

    month = str(3)
    day = str(30)

    if len(month) == 1:
        month = "0" + month

    if len(day) == 1:
        day = "0" + day

    print("get stock price and value")
    get_stock_pv(month, day)
    print("get stock 3 big information")
    get_stock_3big(month, day)

    print("done")