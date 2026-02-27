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

def get_token():
    with open('credentials.json') as f:
        return json.load(f)["token"]

def get_config():
    with open('config.json') as f:
        return json.load(f)
    
class ec_bot(commands.Bot):
    def __init__(self):
        # bot variables
        self.config = get_config()
        self.token = get_token()
        self.database = None
        self.initial_extensions = INITIAL_EXTENSIONS
        super().__init__(command_prefix=self.config["prefixes"], description="Very good description",intents=discord.Intents.all())
    
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
            await asyncio.sleep(20) # changes the status every 20 seconds
            await self.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = f"Difficulty: {self.database.get_current_block()[2]}"))
            await asyncio.sleep(20)
            await self.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = f"Block Height: {self.database.get_current_block()[0]}"))
            await asyncio.sleep(20)
            await self.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = f"Supply: {self.emission_abbreviated()}"))
            await asyncio.sleep(20)

    async def automine_loop(self):
        await self.wait_until_ready()

        while not self.is_closed():
            ids = self.database.get_auto_miners_id()
            if len(ids) == 0:
                print("Detected no autominers! Sleeping for 10 seconds...")
                await asyncio.sleep(10)
                continue
            random.shuffle(ids) # ensures one miner isn't always first, as this game is a first come first serve game
            print(f"Automine Looped\nShuffled IDs:\n{ids}")

            for id in ids:
                reciept = None
                if random.random() <= 2/3: # 2/3 chance to submit share
                    try: _, reciept = self.database.mine(id)
                    except Exception as e:print(e)
                    if random.random() <= .2/3: # 4.44% chance (2/3 * 1/15 = 2/45) to have autominer die
                        user = await self.fetch_user(id)
                        await user.send(f"Uh oh! Your autominer has broken! Run `{self.config["prefixes"][0]}am` to turn it back on.")
                        mining_cog = self.get_cog('Mining')
                        embed = mining_cog.autominer_died_embed(id)
                        await user.send(embed=embed)
                        self.database.update_user_automining_status(id)

                if reciept is None: # no results, just continue
                    continue
                else: # block was broken
                    print(reciept)
                    user_data = self.database.get_user(id)
                    mining_cog = self.get_cog('Mining')
                    curr_block = self.database.get_current_block_relevant_md()
                    await mining_cog.block_broke_embed(user_data, reciept, curr_block)

            await asyncio.sleep(3)

    def emission_abbreviated(self):
        # Tries to get supply and append, if fails just states 0 in supply
        try: supply = int(self.database.get_supply()[0])
        except: return f"0 {self.config["currency"]}"

        # Calculates if supply is large enough to shorten
        # Used modified solution originally by Adam Rosenfield (from: https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings)
        magnitude = 0
        while abs(supply) >= 1000:
            magnitude += 1
            supply /= 1000.0
        
        # If supply is sufficiently large enough to shorten (greater than 1000) will generate formatted string from divided supply num
        if magnitude >= 1: supStr = f"{supply:.2f}"
        else: supStr = supply # Otherwise, just proceed with original number

        return f"{supStr}{['', 'K', 'M', 'B', 'T'][magnitude]} {self.config["currency"]}" # Creates the abbreviated form of number

    def error_embed(self, content):
        # Generates the error message embed with a given descriptor
        return discord.Embed(title=f"Error!", description=f"{content}", color=0xD10000, timestamp=datetime.now())
    
    def error_noacc(self):
        # Generates generic error message embed for users who don't have an account
        return discord.Embed(title=f"Error!", description=f"You don't have an account! Please run `{self.config["prefixes"][0]}create` to get started.", color=0xD10000, timestamp=datetime.now())
    
    def error_nodata(self):
        # Generates generic error message embed for a situation where no data is found
        return discord.Embed(title=f"Error!", description=f"**Nobody here but us chickens!**\nThere is no data to display!", color=0xD10000, timestamp=datetime.now())

    def success_embed(self, content):
        # Generates generic success message embed with a given descriptor
        return discord.Embed(title=f"Success!", description=f"{content}", color=0x008000, timestamp=datetime.now())

    def run(self):
        super().run(self.token, reconnect=True)

if __name__ == '__main__':
    ec = ec_bot()
    ec.run()