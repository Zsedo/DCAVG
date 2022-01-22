from pycoingecko import CoinGeckoAPI
from utils import Diff,fexp
from Binance import Binance
import yaml
import telegram

# configuration
CONFIG_FILE = 'config'
with open(CONFIG_FILE, 'r') as config_file:
    config = yaml.load(config_file, Loader = yaml.BaseLoader)
API_KEY = config["API_KEY"]
SECRET_KEY = config["SECRET_KEY"]
AMOUNT_DCA = float(config["AMOUNT_DCA"])
TELEGRAM_KEY = config["TELEGRAM_KEY"]
# DCA_CHANNEL = config["DCA_CHANNEL"]
PRIVATE_CHAT = config["PRIVATE_CHAT"]
PORTFOLIO = config["PORTFOLIO"]

# init some stuff
# coingecko
cg = CoinGeckoAPI()
# telegram
bot = telegram.Bot(token=TELEGRAM_KEY)

# read top 10 coins (we will only need 5 in end)
top10 = cg.get_coins_markets(vs_currency="USD",per_page=10, order="market_cap_desc")
# stablecoins = cg.get_coins_markets(vs_currency="USD",per_page=10, order="market_cap_desc",category="stablecoin")

# get tickers
tickers10 = [coin["symbol"] for coin in top10]

# eliminate stablecoins
stable_coin_symbols = ["usdt","usdc","busd","dai","ust","tust"]

# take top 5
top5 = [i.upper() for i in Diff(tickers10,stable_coin_symbols)[:5]]

# portfolio
try:
    portfolio_tickers = list(PORTFOLIO.keys())
    portfolio_weights = round(sum(float(i) for i in list(PORTFOLIO.values())),2)
except:
    portfolio_tickers = []
    portfolio_weights = 0

non_defined_portfolio = Diff(top5,portfolio_tickers)
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
        order_data = exchange.create_binance_order(symbol, side, Type, quantity)
        # post to channel
        message_str = yaml.dump(order_data)
        #bot.send_message(text=message_str, chat_id=DCA_CHANNEL)
        # bot.send_message(text="hello", chat_id=DCA_CHANNEL)
        bot.send_message(text=message_str, chat_id=PRIVATE_CHAT)
    except Exception as e:
        print(e)
        bot.send_message(text=message_str, chat_id=PRIVATE_CHAT)