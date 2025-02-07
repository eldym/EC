import discord
import asyncio
import json
import random

from discord.ext import tasks, commands
from datetime import datetime
from database import Database
from cogs.mining import Mining

INITIAL_EXTENSIONS = [
    'cogs.admin',
    'cogs.user',
    'cogs.mining',
    'cogs.blocks',
    'cogs.statistics',
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
            else: print(f"{extension} loaded.")
        # Database
        try: self.database = Database()
        except Exception as e:
            print("ERROR: Database is not initialized!\nException:", e)

        # Status background task
        self.bg_task = self.loop.create_task(self.status_loop())

        # Automining background task
        self.bg_task = self.loop.create_task(self.automine_loop())

    async def status_loop(self):
        # Creates status loop
        await self.wait_until_ready() # Waits til the bot gets built, cus you can't change presence on self
        
        # Loops through the statuses
        while not self.is_closed():
            await self.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = f"made w/ ❤️ by eld_!"))
            await asyncio.sleep(20) # Time interval between changes in status (set to 20 seconds)
            await self.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = f"Difficulty: {self.database.get_current_block()[2]}"))
            await asyncio.sleep(20)
            await self.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = f"Block #{self.database.get_current_block()[0]}"))
            await asyncio.sleep(20)
            await self.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = f"Emission: {self.emission_abbreviated()}"))
            await asyncio.sleep(20)

    def emission_abbreviated(self):
        # Tries to get supply and append, if fails just states 0 in supply
        try: supply = int(self.database.get_supply()[0])
        except: return f"0 {config["currency"]}"

        # Calculates if supply is large enough to shorten
        # Used modified solution originally by Adam Rosenfield (from: https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings)
        magnitude = 0
        while abs(supply) >= 1000:
            magnitude += 1
            supply /= 1000.0
        
        # If supply is sufficiently large enough to shorten (greater than 1000) will generate formatted string from divided supply num
        if magnitude >= 1: supStr = f"{supply:.2f}"
        else: supStr = supply # Otherwise, just proceed with original number

        return f"{supStr}{['', 'K', 'M', 'B', 'T'][magnitude]} {config["currency"]}" # Creates the abbreviated form of number
    
    async def automine_loop(self):
        # Creates automine loop
        await self.wait_until_ready()

        while not self.is_closed():
            for i in self.database.get_auto_miners():
                curr_block = self.database.get_current_block()
                guess, reciept = self.database.mine(i[0])

                if reciept is None: pass
                else: 
                    print('User ID:', i[0], 'broke the block. Guess was:', guess)
                    try: 
                        mining_cog = self.get_cog('Mining')
                        await mining_cog.block_broke_embed(i[0], reciept, curr_block)
                    except Exception as e: print(e)

                    if (random.randint(1,10)==1):
                        print("rip autominer!") # kill user's autominer, send dm
                
                

            await asyncio.sleep(10)

    def error_embed(self, content):
        # Generates the error message embed with a given descriptor
        return discord.Embed(title=f"Error!", description=f"{content}", color=0xFF0000, timestamp=datetime.now())
    
    def run(self):
        super().run(self.token, reconnect=True)

if __name__ == '__main__':
    ec = ec_bot()
    ec.run()