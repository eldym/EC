import discord
import asyncio
import json
import matplotlib.pyplot as plt

from discord.ext import commands
from datetime import datetime

def get_config():
    with open('config.json') as f:
        return json.load(f)

config = get_config()

EMB_COLOUR = 0x000000
DISPLAY_CURRENCY = config["display_currency"]

class Statistics(commands.Cog):
    """
    ## Statistics commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['dp', 'diff'])
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def plot(self, ctx, *data_points):
        # Generates a plot of past block difficulties - default is 30
        defaulted = False

        # Checks if there is a given data points range
        if len(data_points) <= 0 or len(data_points) >= 2: # If no valid number is given
            data_points = 31
            defaulted = True
        elif type(data_points) is tuple: 
            data_points = int(data_points[0])
            if data_points > self.bot.database.get_current_block()[0]: # Checks if range of data being requested would exceed how many blocks currently exist
                embed = self.bot.error_embed("Cannot access block difficulty data that far!")
                data_points = None
        else: 
            embed = self.bot.error_embed("Cannot access block difficulty data!")
            data_points = None

        if data_points is not None:
            difficulties_list = self.__make_plot(data_points) # TODO: use difficulty list data for more statistics in this embed
            if defaulted: data_points -= 1

            embed = discord.Embed(title=f"Past {data_points} Blocks' Difficulty", description=f"A plot of past {data_points} blocks' (*not including current block*) difficulties:", color=EMB_COLOUR, timestamp=datetime.now()) #creates embed
            file = discord.File("chart.png", filename="image.png")
            embed.set_image(url="attachment://image.png")

            await ctx.reply(file=file, embed=embed)
        else: await ctx.reply(embed=embed)
    
    def __difficulties_plot(self, difficulties, begin_index):
        # Creates x axis tickers
        pos = list(range(len(difficulties)))
        new_tickers = list(range(begin_index, begin_index+len(difficulties)))

        # Plots the data of difficulties
        plt.plot(difficulties)

        # Creates custom tickers that properly display the block numbers
        plt.xticks(pos, new_tickers, rotation=90)

        # Labels
        plt.ylabel('Difficulty')
        plt.xlabel('Block #')

        # Parameters
        plt.locator_params(axis='x', nbins=15)

        # Saves plotted chart as a png file
        plt.savefig('chart.png', bbox_inches='tight')
        plt.close() # Resets plt

    def __make_plot(self, amount_of_blocks):
        # Gets block data to make a plot
        all_blocks = self.bot.database.get_blocks_from_current(amount_of_blocks)
        difficulties = []

        # Get beginning index
        i = 0
        begin_index = all_blocks[0][0]
        
        # Appends appropriate data points
        while i < len(all_blocks):
            difficulties.append(all_blocks[i][2])
            i += 1

        # Sends data points to make chart image file
        self.__difficulties_plot(difficulties, begin_index)

        return difficulties
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.reply(f"**Latency:** `{self.bot.latency*1000} ms`")
    
    @commands.command(aliases=['s'])
    async def supply(self, ctx):
        await ctx.reply(f"There is currently {self.bot.get_supply()[0]} {DISPLAY_CURRENCY} in supply.")
    
async def setup(bot):
    await bot.add_cog(Statistics(bot))