import discord
import matplotlib.pyplot as plt
from discord.ext import commands
from datetime import datetime

EMB_COLOUR = 0x000000

class Statistics(commands.Cog):
    """
    ### Statistics Commands
    Commands for viewing currency statistical data.

    - **plot** *{p_blocks}: generates a visualization of block difficulties given a optional past blocks range.
    - **ping**: shows bot ping.
    - **supply**: shows current currency supply.
    """

    def __init__(self, bot):
        self.bot = bot
        self.display_currency = bot.config["display_currency"]

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def plot(self, ctx, *p_blocks):
        """Generates a plot of past block difficulties.\nIf no arguments are provided, default is 30.\nFor 1 argument - # of past blocks to see the difficulties of.\nFor 2 arguments - block difficulties between range."""
        args_count = len(p_blocks)
        # Checks if there is a valid given range of past blocks to check
        
        if args_count == 1:
            try: p_blocks = int(p_blocks[0])
            except: 
                await ctx.reply(embed=self.bot.error_embed("Invalid input! Input of how many past blocks to look back on must be a integer!"))
                return
            if p_blocks > self.bot.database.get_current_block()[0]: # Checks if range of data being requested would exceed how many blocks currently exist
                await ctx.reply(embed=self.bot.error_embed("Cannot access block difficulty data that far!"))
                return
            if p_blocks <= 0:
                await ctx.reply(embed=self.bot.error_embed("Cannot access block difficulty data of less than 0 blocks in range!"))
                return
            begin_index, difficulties_list = self.__make_plot(p_blocks-1)
        elif args_count == 2:
            try: 
                begin_block = int(p_blocks[0])
                end_block = int(p_blocks[1])
            except:
                await ctx.reply(embed=self.bot.error_embed("Invalid input! Input of start/end block(s) must be a integer!"))
                return
            if begin_block <= 0 or end_block <= 0:
                await ctx.reply(embed=self.bot.error_embed("Invalid input! Cannot access block numbers less than or equal to 0."))
                return
            if begin_block >= end_block:
                await ctx.reply(embed=self.bot.error_embed("Invalid input! Start block mustn't be higher or the same compared to the end block to plot!"))
                return
            curr_num = self.bot.database.get_current_block()[0]
            if end_block >= curr_num or begin_block >= curr_num:
                await ctx.reply(embed=self.bot.error_embed("Cannot access block difficulty data that far!"))
                return
            begin_index, difficulties_list = self.__make_plot(begin_block, end_block)
        else:
            p_blocks = 30
            curr_block_height = self.bot.database.get_current_block()[0]
            if p_blocks > curr_block_height: # if the default 30 is larger than current block height, just default to block height
                p_blocks = curr_block_height
            begin_index, difficulties_list = self.__make_plot(p_blocks-1)
        
        difference = difficulties_list[-1] - difficulties_list[0] # current diff - n blocks ago diff
        if difference > 0: emoji_res = "⬆️", "🔴"  
        elif difference < 0: emoji_res = "⬇️", "🟢"
        else: emoji_res = "⏺️", "🟡"
        
        if args_count != 2:
            embed = discord.Embed(title=f"Past {p_blocks} Blocks' Difficulty", description=f"A plot of past {p_blocks} blocks' difficulties has been generated!", color=EMB_COLOUR, timestamp=datetime.now()) #creates embed
            embed.add_field(name="⬆️ Highest Diff. in Range", value=f"`{max(difficulties_list)} @ Block #{difficulties_list.index(max(difficulties_list)) + begin_index}`", inline=True)
            embed.add_field(name="⬇️ Lowest Diff. in Range", value=f"`{min(difficulties_list)} @ Block #{difficulties_list.index(min(difficulties_list)) + begin_index}`", inline=True)
            embed.add_field(name=f"{emoji_res[1]} Difficulty Change Since Block #{begin_index} ({p_blocks} Blocks Ago)", value=f"`{emoji_res[0]} {difference}`", inline=False)
        else:
            embed = discord.Embed(title=f"Difficulties Between Blocks {p_blocks[0]}-{p_blocks[1]}", description=f"A plot of difficulties between blocks {p_blocks[0]}-{p_blocks[1]} has been generated!", color=EMB_COLOUR, timestamp=datetime.now()) #creates embed
            embed.add_field(name="⬆️ Highest Diff. in Range", value=f"`{max(difficulties_list)} @ Block #{difficulties_list.index(max(difficulties_list)) + begin_index}`", inline=True)
            embed.add_field(name="⬇️ Lowest Diff. in Range", value=f"`{min(difficulties_list)} @ Block #{difficulties_list.index(min(difficulties_list)) + begin_index}`", inline=True)
            embed.add_field(name=f"{emoji_res[1]} Difficulty Change Between #{p_blocks[0]} to #{p_blocks[1]}", value=f"`{emoji_res[0]} {difference}`", inline=False)
            
        file = discord.File("chart.png", filename="image.png")
        embed.set_image(url="attachment://image.png")

        await ctx.reply(file=file, embed=embed)
    
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

    def __make_plot(self, begin_block, end_block=None):
        # Gets block data to make a plot
        if end_block is None:
            all_blocks = self.bot.database.get_blocks_diff_from_current(begin_block)
        else:
            all_blocks = self.bot.database.get_blocks_diff_between(begin_block, end_block)

        i = 0
        difficulties = []
        begin_index = all_blocks[0][0]
        # Appends appropriate data points
        while i < len(all_blocks):
            difficulties.append(all_blocks[i][1])
            i += 1

        # Sends data points to make chart image file
        self.__difficulties_plot(difficulties, begin_index)

        return begin_index, difficulties
    
    @commands.command()
    async def ping(self, ctx):
        """Bot ping."""
        await ctx.reply(f"**Latency:** `{self.bot.latency*1000:.2f} ms`")
    
    @commands.command(aliases=['s'])
    async def supply(self, ctx):
        """Current supply of currency."""
        await ctx.reply(f"There is currently {self.bot.database.get_supply()[0]} {self.display_currency} in supply.")
    
async def setup(bot):
    await bot.add_cog(Statistics(bot))