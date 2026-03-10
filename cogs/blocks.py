import discord
from discord.ext import commands

COOLDOWN = 2
EMB_COLOUR = 0x000000

class Blocks(commands.Cog):
    """
    ### Block commands
    Commands and functions pertaining to blocks and information about them.

    - **block / bi / blockinfo** *{block_number}: fetches data on a block, block number field is optional (if empty, defaults to *current* block).
    """

    def __init__(self, bot):
        self.bot = bot
        self.display_currency = bot.config["display_currency"]
        self.emb_thumbnail_link = bot.config["emb_thumbnail_link"]

    @commands.command(aliases=['bi', 'blockinfo'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def block(self, ctx, *block_number):
        """Gives block data given a (optional) block number."""

        if len(block_number) == 0 or len(block_number) > 1:
            block = self.bot.database.get_current_block()
        else:
            try: block = self.bot.database.get_block(int(block_number[0]))
            except: 
                await ctx.reply(embed=self.bot.error_embed("Invalid input for block number!"))
                return
        
        await ctx.reply(embed=self.block_embed(block))

    def block_embed(self, block_data):
        # Generates block information embed if block exists
        if block_data is not None:
            # block data: block_data[0]: block number, block_data[1]: block reward, block_data[2]: difficulty, block_data[3]: difficulty threshold, block_data[4]: block creation time (in unix)
            embed=discord.Embed(title=f"Block #{block_data[0]} Information", description=f"{"*Current block!*" if block_data == self.bot.database.get_current_block() else ""}", color=EMB_COLOUR)
            embed.set_thumbnail(url=self.emb_thumbnail_link)
            embed.add_field(name="💵 Reward Amount", value=f"`{block_data[1]:.6f}` {self.display_currency}", inline=False)
            embed.add_field(name="⚒️ Difficulty", value=f"`{block_data[2]}`", inline=False)
            if block_data == self.bot.database.get_current_block(): embed.add_field(name="🌎 Current Pool Effort", value=f"{self.bot.database.get_pool_share_sum()[0]} Shares", inline=False)
            embed.add_field(name="📊 Diff. Threshold", value=f"`{block_data[3]}`", inline=False)
            embed.add_field(name="⌛ Block Creation Time", value=f"<t:{block_data[4]}:f>", inline=False)
            embed.add_field(name="⏲️ Block Creation Time Unix", value=f"`{block_data[4]}`", inline=False)
            return embed
        else: return self.bot.error_embed("This block does not exist!") # Error embed if block doesn't exist

async def setup(bot):
    await bot.add_cog(Blocks(bot))