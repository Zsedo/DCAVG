Forked from jerryfane/DCAVG

This script buys cryptocurrencies from Binance depending on what you specify in the config. Whatever allocation is not specified, the remainder is split between top5 cryptocurrencies (excluding stablecoins) based on runtime status on coingecko.

Main script is DCAT5.py.
You need to create a markdown file called "config" in the same folder as DCAT5.
You need to have sufficient USDT balance on Binance.

Config structure
API_KEY: your binance api key
SECRET_KEY: your binance secret key
AMOUNT_DCA: amount you will be spending (in USDT)
PORTFOLIO: here you put in the desired allocation into coins, it must sum to 1 or lower (the remained is put into top 5 cryptocurrencies)
    DOT: 0.1
    FTM: 0.05
TELEGRAM_KEY: telegram key of the bot
PRIVATE_CHAT: id of your telegram chat so bot can send you messages

To create a telegram bot, follow these instructions: https://core.telegram.org/bots#6-botfather

To get your chat id:
- Open Telegram
- Search for Telegram Bot Raw (@RawDataBot)
- Open a chat with the bot
- Press START
- Under chat you will find your chat id