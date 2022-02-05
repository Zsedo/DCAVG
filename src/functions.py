# import pandas as pd
# #import time as tm
# from datetime import datetime, time
# from bs4 import BeautifulSoup
# import requests
# from urllib.parse import urljoin, urlencode
# import json

# from telethon.tl.functions.messages import SearchRequest
# from telethon.tl.types import InputMessagesFilterEmpty
# from telethon import TelegramClient, sync
# from telethon import functions, types
# from retrying import retry

# import pandas as pd

from decimal import Decimal
from Binance import Binance
import yaml


def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li2]
    # li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif


def fexp(number):
    (sign, digits, exponent) = Decimal(number).as_tuple()
    return len(digits) + exponent - 1


def main_invest(cg, bot, CONFIG_FILE, DEBUG = False):
    # CONFIG_FILE = 'configurations/users/001_zsedo'
    with open(CONFIG_FILE, 'r') as config_file:
        config = yaml.load(config_file, Loader = yaml.BaseLoader)

    API_KEY = config["API_KEY"]
    SECRET_KEY = config["SECRET_KEY"]
    AMOUNT_DCA = float(config["AMOUNT_DCA"])
    PRIVATE_CHAT = config["PRIVATE_CHAT"]
    PORTFOLIO = config["PORTFOLIO"]
    TOP_N = int(config["TOP_N"])

    # read top N + 20 coins (we will only need 5 in end)
    topNext = cg.get_coins_markets(vs_currency="USD",per_page=TOP_N + 10, order="market_cap_desc")
    # stablecoins = cg.get_coins_markets(vs_currency="USD",per_page=10, order="market_cap_desc",category="stablecoin")

    # get tickers
    tickersN = [coin["symbol"] for coin in topNext]

    # eliminate stablecoins / wrapped
    stable_coin_symbols = ["usdt","usdc","busd","dai","ust","tust", "wbtc", "weth"]

    # take top N
    topN = [i.upper() for i in Diff(tickersN,stable_coin_symbols)[:5]]

    # portfolio
    try:
        portfolio_tickers = list(PORTFOLIO.keys())
        portfolio_weights = round(sum(float(i) for i in list(PORTFOLIO.values())),2)
    except:
        portfolio_tickers = []
        portfolio_weights = 0

    non_defined_portfolio = Diff(topN,portfolio_tickers)
    all_tickers = portfolio_tickers + non_defined_portfolio

    # weights for non defined
    non_defined_weights = round((1.0 - portfolio_weights)/len(non_defined_portfolio),2)


    # create market orders
    exchange = Binance(API_KEY,SECRET_KEY)

    for ticker in all_tickers:
        try:
            symbol = ticker + "USDT"
            side = 'BUY'
            Type = "MARKET"
            # check lot sizes (for step size)
            symbolinfo = exchange.get_exchange_info(symbol=symbol)
            stepsize = float(symbolinfo["symbols"][0]["filters"][2]["stepSize"])
            decimals = -fexp(stepsize)
            # calculate quantity
            price = float(exchange.get_price(symbol)["price"])
            if ticker in portfolio_tickers:
                portfolio_percent = float(PORTFOLIO[ticker])
            else:
                portfolio_percent = non_defined_weights
            amount = AMOUNT_DCA*portfolio_percent
            quantity = round(amount/price,decimals)
            print(symbol)
            print(amount)
            print(price)
            print(quantity)
            print(decimals)
            print(stepsize)
            # create order
            order_data = exchange.create_binance_order(symbol, side, Type, quantity, test = DEBUG)
            # post to channel
            message_str = yaml.dump(order_data)
            # bot.send_message(text=message_str, chat_id=DCA_CHANNEL)
            bot.send_message(text=message_str, chat_id=PRIVATE_CHAT)
        except Exception as e:
            print(e)
            bot.send_message(text=message_str, chat_id=PRIVATE_CHAT)

# def send_message_telegram(client, user_id, output):
#     #destination_channel="https://t.me/{}".format(user)
#     #destination_channel="https://t.me/jerrytest"
#     entity=client.get_entity(int(user_id))
#     #client.send_file(entity=entity,file='screenshot.png',caption=output)
#     client.send_message(entity=entity,message=output)

# def save_buy_info(buy_info, user, bitcoin_price_eur, btc_to_buy, transactTime, exchange='binance'):

#     if exchange == 'binance':
#         orderId = buy_info['orderId']
#         clientOrderId = buy_info['clientOrderId']
#         #transactTime = buy_info['transactTime']
#         quantity_btc = buy_info['origQty']
#         quantity_usd = eur_to_usd(buy_info['cummulativeQuoteQty'])
#         commission_btc = buy_info['fills'][0]['commission']
#         #price_usd = buy_info['fills'][0]['price']
#         price_usd = eur_to_usd(bitcoin_price_eur)
#         tradeId = buy_info['fills'][0]['tradeId']
#         status = 'completed'

#     elif exchange == 'coinbase':
#         orderId = buy_info['order_id'].values[0]
#         clientOrderId = buy_info['order_id'].values[0]
#         #transactTime = buy_info['created_at'].values[0]
#         quantity_btc = buy_info['size'].values[0]
#         quantity_usd = buy_info['usd_volume'].values[0]
#         commission_btc = float(buy_info['fee'].values[0]) / bitcoin_price_eur
#         price_usd = eur_to_usd(bitcoin_price_eur)
#         tradeId = buy_info['trade_id'].values[0]
#         status = 'completed'

#     output = (transactTime, user, quantity_btc, quantity_usd, commission_btc, price_usd, bitcoin_price_eur, btc_to_buy, orderId, clientOrderId, status)
#     data = pd.read_csv('./datasets/data.csv')

#     df = pd.DataFrame(output).T
#     df.columns = ['transactTime', "user", "quantity_btc", "quantity_usd", "commission_btc",
#               'price_usd', "bitcoin_price_eur", "total_btc", "orderId", "clientOrderId", "status"]

#     data = data.append(df, sort=False)
#     data.to_csv('./datasets/data.csv', index=False)


# def save_load_info(transactTime, user, bitcoin_price_usd, bitcoin_price_eur, quantity_btc, quantity_usd, btc_to_buy):
#     status = 'postponed'

#     output = (transactTime, user, quantity_btc, quantity_usd, 0, bitcoin_price_usd, bitcoin_price_eur, btc_to_buy, 0, 0, status)
#     data = pd.read_csv('./datasets/data.csv')

#     df = pd.DataFrame(output).T
#     df.columns = ['transactTime', "user", "quantity_btc", "quantity_usd", "commission_btc",
#               'price_usd', "bitcoin_price_eur", "total_btc", "orderId", "clientOrderId", "status"]

#     data = data.append(df, sort=False)
#     data.to_csv('./datasets/data.csv', index=False)

# def save_price_tick(user, symbol='BTCEUR'):
#     symbol_path = './datasets/{}.csv'.format(symbol)

#     timestamp = exchange_dict[user].get_servertime() #insert name of main user (provided with API keys)
#     bitcoin_price_eur = float(exchange_dict[user].get_price('BTCEUR')['price']) #insert name of main user (provided with API keys)
#     output = timestamp, bitcoin_price_eur

#     SYMBOL = pd.read_csv(symbol_path)
#     df = pd.DataFrame(output).T
#     df.columns = ['timestamp', "price"]

#     SYMBOL = SYMBOL.append(df, sort=False)
#     SYMBOL.to_csv(symbol_path, index=False)


# def usd_to_eur(usd):
#     url_eurusd = "https://api.exchangeratesapi.io/latest"
#     response = requests.get(url_eurusd)
#     soup = BeautifulSoup(response.content, "html.parser")
#     dic = json.loads(soup.prettify())

#     exchange_rate_1eur_eqto = float(dic['rates']['USD'])
#     return float(usd) / exchange_rate_1eur_eqto

# def eur_to_usd(eur):
#     url_eurusd = "https://api.exchangeratesapi.io/latest"
#     response = requests.get(url_eurusd)
#     soup = BeautifulSoup(response.content, "html.parser")
#     dic = json.loads(soup.prettify())

#     exchange_rate_1eur_eqto = float(dic['rates']['USD'])
#     return float(eur) * exchange_rate_1eur_eqto

# #check the time, snapshot needs to be taken at around 00:00 UTC
# def is_time_between(begin_time, end_time, check_time=None):
#     # If check time is not given, default to current UTC time
#     check_time = check_time or datetime.utcnow().time()
#     if begin_time < end_time:
#         return check_time >= begin_time and check_time <= end_time
#     else: # crosses midnight
#         return check_time >= begin_time or check_time <= end_time

# def line_prepender(filename, line):
#     with open(filename, 'r+') as f:
#         content = f.read()
#         f.seek(0, 0)
#         f.write(line.rstrip('\r\n') + '\n' + content)


# def create_excel(user, status, data_path='./datasets/data.csv'):
#     #status = 'completed' or 'postponed'
#     #print('creating excel')

#     df = pd.read_csv(data_path)
#     df['date'] = df['transactTime'].apply(lambda x: datetime.fromtimestamp(int(str(x)[:-3])/100).strftime('%Y-%m-%d %H:%M:%S'))
#     df = df.set_index('date')
#     df['total_btc_value'] = df['total_btc'] * df['price_usd']
#     df3 = df[['user','quantity_btc', 'quantity_usd', 'price_usd', 'bitcoin_price_eur', 'total_btc', 'total_btc_value', 'status']]


#     user_df = df3[df3['user'] == user]
#     df_excel = user_df[user_df.status == status]


#     columns = ['quantity_btc',
#            'bitcoin_price_eur',
#            'price_usd']

#     #df_excel = df_excel[columns][::-1]
#     df_excel = df_excel[columns]
#     df_excel.columns = ['Paid (BTC)', 'BTC Price (EUR)', 'BTC Price (USD)']

#     df_excel['Exchange In (EUR)'] = df_excel['Paid (BTC)'] * df_excel['BTC Price (EUR)']
#     df_excel['Balance (BTC)'] = df_excel['Paid (BTC)'].cumsum()
#     df_excel['Paid (EUR)'] = df_excel['Exchange In (EUR)'].cumsum()
#     df_excel['Balance (EUR)'] = df_excel['Balance (BTC)'] * df_excel['BTC Price (EUR)']
#     df_excel['Balance (USD)'] = df_excel['Balance (BTC)'] * df_excel['BTC Price (USD)']
#     df_excel['Average Price Bought (EUR)'] = df_excel['Paid (EUR)'] / df_excel['Balance (BTC)']
#     df_excel['Average Price Bought (USD)'] = df_excel['Average Price Bought (EUR)'] * (df_excel['BTC Price (USD)'] / df_excel['BTC Price (EUR)'])
#     df_excel['Profit/Loss (EUR)'] = df_excel['Balance (EUR)'] - df_excel['Paid (EUR)']
#     df_excel['Profit/Loss Percentage'] = df_excel['Profit/Loss (EUR)'] / df_excel['Paid (EUR)']

#     cols = ['Paid (BTC)',
#         'Exchange In (EUR)',
#         'Paid (EUR)',
#         'Balance (BTC)',
#         'Balance (EUR)',
#         'Balance (USD)',
#         'BTC Price (EUR)',
#         'BTC Price (USD)',
#         'Average Price Bought (EUR)',
#         'Average Price Bought (USD)',
#         'Profit/Loss (EUR)',
#         'Profit/Loss Percentage'
#     ]

#     df_excel = df_excel[cols]
#     return df_excel


# def create_excel_file(user, data_path):

#     #print('create_excel_file')

#     with pd.ExcelWriter('./excel_files/{}.xlsx'.format(user)) as writer:
#         create_excel(user, 'postponed', data_path).to_excel(writer, sheet_name='Postponed')
#         create_excel(user, 'completed', data_path).to_excel(writer, sheet_name='Completed')
