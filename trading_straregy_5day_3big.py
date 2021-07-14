import pyodbc
import pandas as pd
import datetime
import crawler.tool as crawler_tool
import matplotlib.pyplot as plt
from matplotlib import gridspec


conn = pyodbc.connect("DRIVER={SQL Server};SERVER=DESKTOP-OKF0JOA;DATABASE=stock_information")
cursor = conn.cursor()


def current_price(stock_id):
    stock_info = crawler_tool.url_retry_json(
        "https://ws.api.cnyes.com/ws/api/v1/charting/history?resolution=M&symbol=TWS%3A" +
        str(stock_id) + "%3ASTOCK&quote=1")

    c_price = stock_info['data']['c'][0]

    return c_price


def plot_stock_pv(s_input):

    delta_day = str(datetime.date.today() - datetime.timedelta(days=20))
    if type(s_input) is int:
        stock_id = str(s_input)
        sql_cmd = "select * from stock_pv where ID = '" + stock_id + "' and Time > '" +delta_day + "' order by Time"
    elif type(s_input) is str:
        sql_cmd = "select * from stock_pv where Name = '" + s_input + "' and Time > '" +delta_day + "' order by Time"
    else:
        print("input stock id or name")

    delta_price = pd.read_sql(sql_cmd, conn)
    stock_id = str(int(delta_price["ID"][0]))
    five_average = round(delta_price[["收盤價"]].astype(float).rolling(5,min_periods=5).mean(),2)

    delta_price["average_5"] = five_average.values
    stock_to_print = delta_price[["Time", "收盤價", "average_5"]].drop([0,1,2,3])
    c_price = current_price(stock_id)

    new_info = pd.DataFrame({stock_to_print.columns[0]: str(datetime.date.today()),
                             stock_to_print.columns[1]: c_price,
                             stock_to_print.columns[2]: (stock_to_print["收盤價"][-4:].astype(float).sum()+float(c_price))/5
                            }, index=[0])

    stock_to_print = stock_to_print.append(new_info).reset_index().drop(["index"],axis=1)

    # current price color
    if c_price > float(delta_price["收盤價"].values[-1]):
        c_price_color = "red"
    else:
        c_price_color = "green"

    stock_time = list(t.split("-")[1]+t.split("-")[2] for t in stock_to_print["Time"])

    sql_cmd = "select * from stock_3big where ID = '" + stock_id + "' and Time > '" + delta_day + "' order by Time"
    delta_3big = pd.read_sql(sql_cmd, conn).drop([0, 1, 2, 3])



    fig = plt.figure()
    plt.rcParams['font.sans-serif'] = ['SimSun']   # 替換sans-serif字型）
    plt.rcParams['axes.unicode_minus'] = False

    spec = gridspec.GridSpec(ncols=2, nrows=1, width_ratios=[3, 1])
    ax0 = fig.add_subplot(spec[0])
    ax0_1 = ax0.twinx()
    ax0.plot(stock_time, stock_to_print["收盤價"].astype(float), label="股價")
    ax0.plot(stock_time, stock_to_print["average_5"].astype(float), color="orange", label="5日均")
    ax0.legend(loc="best", fontsize=12)
    ax0.set_title(delta_price["Name"][0])

    ax0_1.bar(stock_time[0:-1], delta_3big["三大法人買賣超"], alpha=0.2, color="green")
    ax0.grid(axis="both")  # 格線

    ax1 = fig.add_subplot(spec[1])
    ax1.text(0, 0.9,"現價: ", fontsize=12)
    ax1.text(0.1, 0.82, c_price, fontsize=16,color=c_price_color)
    ax1.text(0, 0.7,"突破五日價: ", fontsize=12)
    ax1.text(0.1, 0.62, round(delta_price["收盤價"][-4:].astype(float).mean(), 2), fontsize=16)
    ax1.axis("off")
    plt.show()



