import discord
import asyncio
import json
import matplotlib.pyplot as plt

from discord.ext import commands
from datetime import datetime

EMB_COLOUR = 0x000000

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
    
    def __difficulties_plot(self, difficulties, beginIndex):
        # Creates x axis tickers
        pos = list(range(len(difficulties)))
        newTickers = list(range(beginIndex, beginIndex+len(difficulties)))

        # Plots the data of difficulties
        plt.plot(difficulties)

        # Creates custom tickers that properly display the block numbers
        plt.xticks(pos, newTickers, rotation=90)

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
        allBlocks = self.bot.database.get_all_blocks()
        difficulties = []

        # Get beginning index
        if len(allBlocks) > amount_of_blocks:
            i = len(allBlocks) - amount_of_blocks
        else: i = 0

        beginIndex = i
        
        # Appends appropriate data points
        while i < len(allBlocks):
            difficulties.append(allBlocks[i][2])
            i += 1

        # Sends data points to make chart image file
        self.__difficulties_plot(difficulties, beginIndex)

        return difficulties
    
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def ping(self, ctx):
        pass # TODO add this
    
async def setup(bot):
    await bot.add_cog(Statistics(bot))