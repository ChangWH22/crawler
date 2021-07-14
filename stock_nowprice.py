import json
import pandas as pd
import time
import datetime
import crawler.tool as crawler_tool

def stock_intime(ID, end_time):
    stock_id = []
    name = []
    deal_price = []
    deal_count = []
    count = []
    open_price = []
    close_price = []
    stock_time = []

    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_" + str(ID) + ".tw&json=1&delay=0&_=1599188567060"


    while datetime.datetime.strptime(time.strftime("%H%M", time.localtime()), "%H%M") < datetime.datetime.strptime(end_time, "%H%M"):
        try:
            r = crawler_tool.url_retry_json(url)
            stock_id.append(r['msgArray'][0]["c"])
            name.append(r['msgArray'][0]["n"])
            deal_price.append(r['msgArray'][0]["z"])
            deal_count.append(r['msgArray'][0]["tv"])
            count.append(r['msgArray'][0]["v"])
            open_price.append(r['msgArray'][0]["o"])
            close_price.append(r['msgArray'][0]["y"])
            stock_time.append(r['queryTime']['sysTime'])

            print(r['msgArray'][0]["n"] +"  "+ str(r['msgArray'][0]["z"])+"  "+\
                     str(r['msgArray'][0]["tv"])+"  "+r['msgArray'][0]["v"]+"  "+ str(float(r['msgArray'][0]["o"]))+\
                    "  "+r['queryTime']['sysTime'])
            time.sleep(5)
        except TypeError:
            continue

    df = pd.DataFrame({'股票代號': stock_id, '公司簡稱': name, '當盤成交價': deal_price,
                      '當盤成交量': deal_count, '累積成交量': count, '開盤價': open_price,
                       '昨收價': close_price, '時間': stock_time})

    df_json = {"stock_id": stock_id[0],
               "name": name[0],
               "deal_price": deal_price,
               "deal_count": deal_count,
               "count": count,
               "open_price": open_price[0],
               "close_price": close_price[0],
               "stock_time": stock_time}

    j = json.dumps(df_json)  ###dict-json
    local_time = time.strftime("%m%d", time.localtime())
    save_json = "D:/User/Desktop/corpus/stock/" + name[0] + "_" + str(local_time) + ".json"
    save_csv = "D:/User/Desktop/corpus/stock/" + name[0] + "_" + str(local_time) + ".csv"

    df.to_csv(save_csv,encoding="utf-8")

    with open(save_json, 'w', encoding='utf-8') as f:  ###存檔
        json.dump(j, f)

    return df


def get_stock_price(stock_number="2303", buy='noon'):

    stock_info = crawler_tool.url_retry_json("https://ws.api.cnyes.com/ws/api/v1/charting/history?resolution=M&symbol=TWS%3A"+
                                             stock_number + "%3ASTOCK&quote=1")

    now_time = str(datetime.datetime.today().hour)+":" + str(datetime.datetime.today().minute)+":"+str(datetime.datetime.today().second)
    now_info = pd.DataFrame({"ID": [stock_number],
                             "name": [stock_info['data']['quote']['200009']],
                             "price": [stock_info['data']['c'][0]],
                             "quantity": [stock_info['data']['quote']['800001']],
                             "time": [now_time]})

    if buy == 'noon':
        print("Id: ", stock_number,
              "  name: ", stock_info['data']['quote']['200009'],
              "  price: :", stock_info['data']['c'][0],
              "  Quantity: ", stock_info['data']['quote']['800001'])
    else:
        benifit = float(stock_info['data']['c'][0])*1000*0.995575 - float(buy)*1000*1.001425
        print(stock_info['data']['quote']['200009'], "現價: ", stock_info['data']['c'][0], "買在: ", buy
              , "損益:  ", "{:.1f}".format(benifit))

    return now_info


def get_stock_pv_cmoney():
    url = "https://www.cmoney.tw/follow/channel/getdata/GetStockOtherInfo?stockId=2303&channelId=103123&_=1612145325218"
    info = crawler_tool.url_retry_json(url)
    print('Id: ', info['StockInfo']['Id'],
          '  Name: ', info['StockInfo']['Name'],
          '  Price: ', info['StockInfo']['Price'],
          '  Quantity: ', info['StockInfo']['Quantity'])

    now_time = str(datetime.datetime.today().hour)+":" + str(datetime.datetime.today().minute)+":"+str(datetime.datetime.today().second)
    now_info = pd.DataFrame({"ID": [info['StockInfo']['Id']],
                             "name": [info['StockInfo']['Name']],
                             "price": [info['StockInfo']['Price']],
                             "quantity": [info['StockInfo']['Quantity']],
                             "time": [now_time]})
    return now_info


df = pd.DataFrame({"ID": [],
                   "name": [],
                   "price": [],
                   "quantity": [],
                   "time":  []})
retry_time = 1
trytimes = 10  # 重複連接
while retry_time < trytimes:
    df = df.append(get_stock_pv_cmoney(), ignore_index=True)
    time.sleep(10)
    df = df.append(get_stock_price("2002"), ignore_index=True)
    time.sleep(50)
    retry_time += 1
    print("connecting time: ", retry_time)
    print("\n\n")
    #get_stock_price("2603")

