import discord
import asyncio
import json

from discord.ext import commands
from datetime import datetime

def get_config():
    with open('config.json') as f:
        return json.load(f)

config = get_config()

EMB_COLOUR = 0x000000
DISPLAY_CURRENCY = config["display_currency"]

class Leaderboards(commands.Cog):
    """
    ## Mining commands
    """

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['lb', 'leader', 'board'])
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def leaderboard(self, ctx, lbType, *page):
        # Gives the user leaderboards

        # Checks if it should default to page 1 (if there is no given page number or invalid input)
        if len(page) <= 0 or len(page) >= 2:
            page = 1
        elif type(page) is tuple:
            page = int(page[0])

        # Checks what the user inputs
        bOptions = ['b', 'bal', 'balance']
        sOptions = ['s', 'solo']
        pOptions = ['p', 'pool']

        data = None

        # Checks the typing of leaderboard requested
        if lbType.lower() in bOptions:
            lbType = 'Balance' # To send off to embed builder to specify
            data = self.bot.database.get_balances_descending() # Gets database data
        elif lbType.lower() in sOptions:
            lbType = 'Solo Block'
            data = self.bot.database.get_solo_block_descending()
        elif lbType.lower() in pOptions:
            lbType = 'Pool Block'
            data = self.bot.database.get_pool_block_descending()
        
        # Replies built leaderboard embed
        if len(data) > 0 or data is None:
            embed = await self.lb_embed(data, lbType, page)
            if embed is not None:
                await ctx.reply(embed=embed)
            else:
                await ctx.reply(embed = self.bot.error_embed("**Nobody here but us chickens!**\nThere is no data to display!"))
        else:
            await ctx.reply(embed = self.bot.error_embed("**Nobody here but us chickens!**\nThere is no data to display!"))
    
    async def lb_embed(self, data, lbType, page):
        # Generates leaderboard embeds

        # Calculates index ranges from given page number
        if type(page) is int and page >= 1: 
            startIndex = (page*10) - 10
            endIndex = (page*10)
        else: 
            startIndex = 0
            endIndex = 10
        
        # Gets the users between the index points
        lbData = data[startIndex:endIndex]

        # If there is results from the given page number
        if len(lbData) >= 1:
            # Determines whether it should be displaying the currency or blocks for lb building
            if lbType == "Balance": 
                whichType = DISPLAY_CURRENCY
                whichNumber = 1 # to display currency
            else: 
                whichType = "block(s)"
                if lbType == "Pool Block":
                    whichNumber = 2 # to display pool
                else:
                    whichNumber = 3 # to display solo

            # Building embed
            embed = discord.Embed(title=f"{lbType} Leaderboard", color=EMB_COLOUR, timestamp=datetime.now())
            startIndex += 1
            for i in lbData:
                username = i[5]
                embed.add_field(name=f"{startIndex}. {username.replace('_', '\\_')} (`{i[0]}`)", value=f"{i[whichNumber]} {whichType}", inline=False)
                startIndex += 1
            
            # Shows page number
            embed.set_footer(text=f"Page {page}")

            # Returns final leaderboard embed
            return embed
        else:
            return None # If there are no results, send None

async def setup(bot):
    await bot.add_cog(Leaderboards(bot))