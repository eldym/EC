import discord
from discord.ext import commands
from datetime import datetime

EMB_COLOUR = 0x000000
BAL_OPTIONS = ['b', 'bal', 'balance']
BLOCK_OPTIONS = ['block', 'blocks']

class Leaderboards(commands.Cog):
    """
    Mining commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.display_currency = bot.config["display_currency"]
    
    @commands.command(aliases=['lb', 'leader', 'board'])
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def leaderboard(self, ctx, lb_type, *page):
        """Gives the leaderboards given a leaderboard type and optionally a page number."""

        # Checks if it should default to page 1 (if there is no given page number or invalid input)
        if len(page) == 0 or len(page) > 1:
            page = 1
        if type(page) is tuple:
            page = int(page[0])

        data = None
        # Checks the typing of leaderboard requested
        if lb_type.lower() in BAL_OPTIONS:
            lb_type = 'Balance' # To send off to embed builder to specify
            data = self.bot.database.get_balances_descending(offset=page-1) # Gets database data
        elif lb_type.lower() in BLOCK_OPTIONS:
            lb_type = 'Blocks'
            data = self.bot.database.get_blocks_descending(offset=page-1)
        
        # Replies built leaderboard embed
        if len(data) > 0 or data is None:
            embed = await self.lb_embed(data, lb_type, page) # generate embed
            if embed is not None:
                await ctx.reply(embed=embed)
            else:
                await ctx.reply(embed = self.bot.error_nodata())
        else:
            await ctx.reply(embed = self.bot.error_nodata())
    
    async def lb_embed(self, data, lb_type, page):
        # Generates leaderboard embeds
        embed = None
        # Calculates index ranges from given page number
        if type(page) is int and page >= 1: 
            startIndex = (page*10) - 10
            endIndex = (page*10)
        else: 
            startIndex = 0
            endIndex = 10
        
        # Gets the users between the index points
        lbData = data

        # If there is results from the given page number
        if len(lbData) >= 1:
            # Building embed
            embed = discord.Embed(title=f"{lb_type} Leaderboard", color=EMB_COLOUR, timestamp=datetime.now())
            startIndex += 1
            for i in lbData:
                username = i[2]
                embed.add_field(name=f"{startIndex}. {username.replace('_', '\\_')} (`{i[0]}`)", value=f"{i[1]} {self.display_currency if lb_type == "Balance" else "block(s)"}", inline=False)
                startIndex += 1
            
            # Shows page number
            embed.set_footer(text=f"Page {page}")

        # Returns leaderboard embed
        return embed

async def setup(bot):
    await bot.add_cog(Leaderboards(bot))