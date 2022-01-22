# from pycoingecko import CoinGeckoAPI
# from utils import Diff,fexp
from Binance import Binance
import yaml
import json
# import telegram

# configuration
CONFIG_FILE = 'config'
with open(CONFIG_FILE, 'r') as config_file:
    config = yaml.load(config_file, Loader = yaml.BaseLoader)
API_KEY = config["API_KEY"]
SECRET_KEY = config["SECRET_KEY"]
AMOUNT_DCA = float(config["AMOUNT_DCA"])
TELEGRAM_KEY = config["TELEGRAM_KEY"]
DCA_CHANNEL = config["DCA_CHANNEL"]
PRIVATE_CHAT = config["PRIVATE_CHAT"]
PORTFOLIO = config["PORTFOLIO"]

exchange = Binance(API_KEY,SECRET_KEY)

balances = exchange.get_wallet_balance()

# wallet balances
wallet = dict()
for coin in balances:
    amount = float(coin["free"])
    if amount > 0.0:
        wallet[coin["coin"]] = amount

# to usdt
symbols = []
for w in wallet:
    if w != "USDT":
        symbols.append(w + "USDT")


smbls = str(json.dumps(symbols)).replace(" ","")

prices = exchange.get_exchange_info(symbols = smbls)


for s in prices["symbols"]:
    s["symbol"]
    s