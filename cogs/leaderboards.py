import discord
from discord.ext import commands
from datetime import datetime

EMB_COLOUR = 0x000000
BAL_OPTIONS = ['b', 'bal', 'balance']
BLOCK_OPTIONS = ['bl', 'block', 'blocks']

class Leaderboards(commands.Cog):
    """
    Mining commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.display_currency = bot.config["display_currency"]
    
    @commands.command(aliases=['lb'])
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def leaderboard(self, ctx, *args):
        """Gives the leaderboard given user inputted parameters.\n- If no parameters are provided, deafults to first page of balance leaderboard.\n- If one parameter is provided, it must be either an integer or string (ie. !lb 2 or !lb blocks).\n- If two are provided, they must be a pair of an integer and string (ie. !lb bal 3). The position of the parameter types does not matter."""

        if len(args) == 0: # no given parameters (ex. !lb -> balance leaderboard, page 1)
            lb_type = "b"
            page = 1

        elif len(args) == 1: # given 1 parameter
            if args[0].isdigit(): # ex. !lb 5 -> balance leaderboard, page 5
                page = int(args[0])
                lb_type = "b"
            elif args[0].isalpha(): # ex. !lb blocks -> blocks leaderboard, page 1
                page = 1
                lb_type = args[0].lower()
            else:
                await ctx.reply(embed=self.bot.error_embed("Invalid input for leaderboard command!"))
                return

        elif len(args) == 2: # given 2 parameters
            if args[0].isdigit(): # ex. !lb 5 bal -> balance leaderboard, page 5
                page = int(args[0])
                lb_type = args[1].lower()
            elif args[0].isalpha(): # ex. !lb bal 5 -> balance leaderboard, page 5
                lb_type = args[0].lower()
                page = int(args[1])
            else:
                await ctx.reply(embed=self.bot.error_embed("Invalid inputs for leaderboard command!"))
                return

        else: # parameters length is greater than 2, just deny
            await ctx.reply(embed=self.bot.error_embed("Too many inputs for leaderboard command!\nThis command only takes two positional arguments."))
            return

        if page <= 0: # page number obviously cannot be 0 or less
            await ctx.reply(embed = self.bot.error_nodata())
            return
            
        data = None
        # Checks the typing of leaderboard requested
        if lb_type in BAL_OPTIONS:
            lb_type = 'Balance' # Variable gets turned "proper" send off to embed builder for the title of the embed
            data = self.bot.database.get_balances_descending(offset=page-1) # Gets database data
        elif lb_type in BLOCK_OPTIONS:
            lb_type = 'Blocks'
            data = self.bot.database.get_blocks_descending(offset=page-1)
        else:
            await ctx.reply(embed=self.bot.error_embed("Invalid leaderboard type!"))
            return

        # Replies built leaderboard embed
        if data is None or len(data) == 0: # requested leaderboard page does not have any data  
            await ctx.reply(embed = self.bot.error_nodata())
        else: # requested leaderboard page has data
            embed = await self.lb_embed(data, lb_type, page) # generate embed
            await ctx.reply(embed=embed)
    
    async def lb_embed(self, data, lb_type, page):
        # Generates leaderboard embeds
        embed = None
        # Calculates index ranges from given page number
        if type(page) is int and page >= 1: 
            start_index = (page*10) - 10
        else: 
            start_index = 0
        
        # Gets the users between the index points
        lb_data = data

        # If there is results from the given page number
        if len(lb_data) >= 1:
            # Building embed
            embed = discord.Embed(title=f"{lb_type} Leaderboard", color=EMB_COLOUR, timestamp=datetime.now())
            start_index += 1
            for i in lb_data:
                username = i[2]
                embed.add_field(name=f"{start_index}. {username.replace('_', '\\_')} (`{i[0]}`)", value=f"{i[1]} {self.display_currency if lb_type == "Balance" else "block(s)"}", inline=False)
                start_index += 1
            
            # Shows page number
            embed.set_footer(text=f"Page {page}")

        # Returns leaderboard embed
        return embed

async def setup(bot):
    await bot.add_cog(Leaderboards(bot))