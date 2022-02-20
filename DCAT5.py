from functions import main_invest, Diff
import telegram
from pycoingecko import CoinGeckoAPI
import yaml
from os import listdir

# shared config
SHARED_CONFIG_FILE = 'configurations/shared'
with open(SHARED_CONFIG_FILE, 'r') as config_file:
    shared_config = yaml.load(config_file, Loader = yaml.BaseLoader)

TELEGRAM_KEY = shared_config["TELEGRAM_KEY"]
DEBUG_CHANNEL = shared_config["DEBUG_CHANNEL"]

# init some stuff
# coingecko
cg = CoinGeckoAPI()
# telegram
bot = telegram.Bot(token=TELEGRAM_KEY)

# read users
configs = listdir("configurations/users")
configs = Diff(configs, ["000_template.yaml"])
configs.sort()

configs = ["configurations/users/" + config for config in configs]

for config_path in configs:
    main_invest(cg = cg, bot = bot, CONFIG_FILE = config_path, DEBUG_CHANNEL = DEBUG_CHANNEL, DEBUG = False)