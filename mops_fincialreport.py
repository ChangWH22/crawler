from bs4 import BeautifulSoup
import pandas as pd
from tool import clean_html, url_retry_mops
import re
import time
import random
import os


def mkdir(location):

    path = "D:/User/Desktop/corpus/report/" + location
    if os.path.exists(path):
        print(path + '....目錄已存在')
    else:
        os.makedirs(path)
        print(path + '....建立成功')
'''
url = "https://mops.twse.com.tw/server-java/t164sb01?step=3&SYEAR=2020&file_name=tifrs-fr1-m1-ci-cr-1215-2020Q4.html"
year = '2020'
quarter = 'Q4'
'''
def get_report(url, stock, year, quarter):
    def clean_report(file):
        file = re.sub(r"<[^>]+>", "", str(file))
        file = re.sub(r"\s{0, }", "", file)
        file = re.sub("N", "", file)
        return file
    r = url_retry_mops(url)
    r.encoding = "cp950"
    soup = BeautifulSoup(r.text, "lxml")
    content = soup.find("div", attrs={"class": "content"}).select("tr")

    # try 消除html標籤 利用尋找表中元素位置來抓資料收集始末點 有位置始末點後 創建list 抓代號、 中文、值(多年分) 合併dataframe 或 dict

    for i in range(len(content)):
        tem = clean_html(str(content[i]))
        tem = re.sub(r"[a-zA-Z]", "", tem)
        tem = re.sub(r"\s+", "", tem)
        content[i] = tem

    bs = content.index("資產負債表")
    soci = content.index("綜合損益表", bs, len(content))
    socf = content.index("現金流量表", soci, len(content))
    socie = content.index("當期權益變動表", soci, len(content))

    if "利息收入" in content and "其他收入" in content :
        lizi = content.index("利息收入", socf, len(content))
        otic = content.index("其他收入", socf, len(content))
        if lizi < otic:
            otic = lizi
    elif "其他收入" in content:
        otic = content.index("其他收入", socf, len(content))
    elif "其他利益及損失" in content:
        otic = content.index("其他利益及損失", socf, len(content))
    elif "利息收入" in content:
        otic = content.index("利息收入", socf, len(content))
    else:
        otic = len(content)

    content = soup.find("div", attrs={"class": "content"}).select("tr")

    file_name = str(stock) + "_" + str(year) + str(quarter)

    # 資產負債表

    num = []; zh = []; val = []

    for i in range(bs, soci):
        try:
            num.append(content[bs + i].find("td", attrs={"style": "text-align:center"}).string)
            zh.append(re.sub(r"\s+", "", content[bs + i].find("span", attrs={"class": "zh"}).string))
            val.append(content[bs + i].find_all("td", attrs={"class": "amt"})[0])

        except AttributeError:
            num.append("-")
            zh.append("-")
            val.append(content[bs + i].select("th"))

    colname = list(map(clean_report, val[1]))[0:3]
    val = list(map(clean_report, val[2:]))
    df_0 = pd.DataFrame({colname[0]: num[2:], colname[1]: zh[2:], colname[2]: val})
    save_add = "D:/User/Desktop/corpus/report/"+year+quarter+"/balance_sheet/" + file_name + ".csv"
    df_0.to_csv(save_add, encoding="CP950")

    # 現金流量表
    num = []; zh = []; val = []

    for i in range(socf, socie):
        try:
            num.append(content[bs + i].find("td", attrs={"style": "text-align:center"}).string)
            zh.append(re.sub(r"\s+", "", content[bs + i].find("span", attrs={"class": "zh"}).string))
            val.append(content[bs + i].find_all("td", attrs={"class": "amt"})[0])
        except AttributeError:
            num.append("-")
            zh.append("-")
            val.append(content[bs + i].select("th"))

    colname = list(map(clean_report, val[1]))[0:3]

    val = list(map(clean_report, val[2:]))
    df_2 = pd.DataFrame({colname[0]: num[2:], colname[1]: zh[2:], colname[2]: val})
    save_add = "D:/User/Desktop/corpus/report/"+year+quarter+"/cash_flow/" + file_name + ".csv"
    df_2.to_csv(save_add, encoding="CP950")

    # 綜合損益表

    num = []; zh = []; val = []

    for i in range(soci, socf):
        try:
            num.append(content[bs + i].find("td", attrs={"style": "text-align:center"}).string)
            zh.append(re.sub(r"\s+", "", content[bs + i].find("span", attrs={"class": "zh"}).string))
            val.append(content[bs + i].find_all("td", attrs={"class": "amt"})[0])

        except AttributeError:
            num.append("-")
            zh.append("-")
            val.append(content[bs + i].select("th"))


    colname = list(map(clean_report, val[1]))[0:3]
    val = list(map(clean_report, val[2:]))
    df_1 = pd.DataFrame({colname[0]: num[2:], colname[1]: zh[2:], colname[2]: val})

    # 營業外收入及支出
    try:
        num = []
        zh = []
        val = []

        for i in range(otic, len(content)):
            if len(content[bs + i].find_all("td")) > 0:
                num.append(content[bs + i].find_all("td")[0])
                zh.append(content[bs + i].find_all("td")[1])
                val.append(content[bs + i].find_all("td")[2:])

            else:
                num.append("-")
                zh.append("-")
                val.append(content[bs + i].select("th"))

        colname = list(map(clean_report, val[1]))[0:3]
        num_ = []; zh_ = []; val_ = []

        for i in range(2, len(num)):
            if len(clean_report(zh[i])) > 1:
                num_.append(clean_report(num[i]))
                zh_.append(clean_report(zh[i]))
                val_.append(clean_report(val[i][0]))

        df_3 = pd.DataFrame({colname[0]: num_, colname[1]: zh_, colname[2]: val_})

        if colname[2] in df_1.columns[2]:
            df_3.columns = [df_1.columns[0], df_1.columns[1], df_1.columns[2]]
            df_1c3 = pd.concat([df_1, df_3], join="outer").drop_duplicates(keep="first", subset=["代號Code"])
        else:
            print("年份錯誤")
    except:
        print("營業外收入..noon_file")
        df_1c3 = df_1

    save_add = "D:/User/Desktop/corpus/report/"+year+quarter+"/income_statement/" + file_name + ".csv"
    df_1c3.to_csv(save_add, encoding="CP950")




'''
目標 excel 一欄放url前述 若下載檔案複製欄位到下一欄， 所有檔案下載完成刪掉那一欄 
'''

## income statement table includ single quarter and cum quarter


def auto_run(year, quarter):

    mkdir(year + quarter)
    mkdir(location=year + quarter + "/balance_sheet")
    mkdir(location=year + quarter + "/income_statement")
    mkdir(location=year + quarter + "/cash_flow")

    stock_list = pd.read_csv("D:/User/Desktop/corpus/mops/stock_normal_web1.csv", encoding="cp950")

    if stock_list.shape[1] < 6:
        stock_list["new"] = ""

    for i in range(0, stock_list.shape[0]):
        if not str(stock_list.loc[stock_list.index[i], stock_list.columns[4]]) == 'nan':
            stock = str(stock_list.loc[stock_list.index[i], stock_list.columns[0]])
            url = stock_list.loc[stock_list.index[i], stock_list.columns[4]] + stock + "-" + str(year) + str(quarter) + ".html"
            print(url)
            try:
                get_report(url, stock, year, quarter)
                stock_list.loc[stock_list.index[i], stock_list.columns[5]] = stock_list.loc[stock_list.index[i], stock_list.columns[4]]
                stock_list.loc[stock_list.index[i], stock_list.columns[4]] = ""
                sleep = 3 * random.uniform(0, 3)
                print(stock_list.loc[stock_list.index[i], stock_list.columns[0]], "...sleep for ", sleep)
                time.sleep(sleep)
            except:
                print(stock_list.loc[stock_list.index[i], stock_list.columns[0]], "error ")
                pass
        stock_list.to_csv("D:/User/Desktop/corpus/mops/stock_normal_web.csv", encoding="cp950", index=False)




if __name__ == '__main__':
    auto_run(year="2020", quarter="Q4")