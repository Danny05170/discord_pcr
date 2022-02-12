from bot import bot
import nest_asyncio
from plugins.jjc_watcher import initialize

if __name__ == '__main__':
    import json
    with open('./config.json') as f:
        config = json.load(f)
    initialize(config)
    nest_asyncio.apply()
    bot.run(config['token'])
