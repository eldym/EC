import discord
import asyncio
import json

from discord.ext import tasks, commands
from datetime import datetime
from database import Database

INITIAL_EXTENSIONS = [
    'cogs.admin',
    'cogs.user',
    'cogs.mining',
    'cogs.pool',
    'cogs.transactional',
    'cogs.leaderboards'
]
    
def get_config():
    with open('config.json') as f:
        return json.load(f)
    
def get_token():
    with open('credentials.json') as f:
        return json.load(f)

config = get_config()
token = get_token()

class ec_bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config["prefixes"], description="Very good description",intents=discord.Intents.all())
        self.owner_id = config["admin_id"]
        self.cooldown = config["cooldown"]
        self.token = token["token"]
        self.initial_extensions = INITIAL_EXTENSIONS
        self.database = None
    
    async def on_ready(self):
        # Starts up the bot!
        print('Waking up!')
        print(f"EC is online! :3\nLogged in as:\nUsername: \"{self.user.name}\"\nID: {self.user.id}")

    async def setup_hook(self) -> None:
        # Sets it all up
        for extension in self.initial_extensions:
            try: await self.load_extension(extension)
            except Exception as e: print(f"ERROR: Extension {extension} did not load!\nException:", e)
        
        # Database
        try: self.database = Database()
        except Exception as e:
            print("ERROR: Database is not initialized!\nException:", e)

        # Status background task
        self.bg_task = self.loop.create_task(self.status())

    async def status(self):
        # Creates status loop
        await self.wait_until_ready() # Waits til the bot gets built, cus you can't change presence on self

        # Changes bot status every 20 seconds from status list
        statuses = ["made w/ ❤️ by eld_!", f"EC difficulty: ", f"block #"] # Add/edit status selection to your choosing
        
        # Loops through the statuses
        for status in statuses:
            await self.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = f"{status}"))
            await asyncio.sleep(20) # Time interval between changes in status (set to 20 seconds)
    
    def error_embed(self, content):
        # Generates the error message embed with a given descriptor
        return discord.Embed(title=f"Error!", description=f"{content}", color=0xFF0000, timestamp=datetime.now())
    
    def run(self):
        super().run(self.token, reconnect=True)

if __name__ == '__main__':
    ec = ec_bot()
    ec.run()