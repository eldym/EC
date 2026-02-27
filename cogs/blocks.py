import discord
from discord.ext import commands

COOLDOWN = 2
EMB_COLOUR = 0x000000

class Blocks(commands.Cog):
    """
    Block commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.display_currency = bot.config["display_currency"]
        self.emb_thumbnail_link = bot.config["emb_thumbnail_link"]

    @commands.command(aliases=['bi', 'blockinfo'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def block(self, ctx, block_number):
        """Gives block data given a block number."""
        block = self.bot.database.get_block(block_number)
        await ctx.reply(embed=self.block_embed(block))

    @commands.command(aliases=['cb', 'current', 'currentblock'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def current_block(self, ctx):
        """Gives the current block data."""
        curr = self.bot.database.get_current_block()
        await ctx.reply(embed=self.block_embed(curr))

    def block_embed(self, blockData):
        # Generates block information embed if block exists
        if blockData is not None:
            embed=discord.Embed(title=f"Block #{blockData[0]} Information", description=f"{"*Current block!*" if blockData == self.bot.database.get_current_block() else ""}", color=EMB_COLOUR)
            embed.set_thumbnail(url=self.emb_thumbnail_link)
            embed.add_field(name="💵 Reward Amount", value=f"`{blockData[1]:.6f}` {self.display_currency}", inline=False)
            embed.add_field(name="⚒️ Difficulty", value=f"`{blockData[2]}`", inline=False)
            if blockData == self.bot.database.get_current_block(): embed.add_field(name="🌎 Current Pool Effort", value=f"{self.bot.database.get_pool_share_sum()[0]} Shares", inline=False)
            embed.add_field(name="📊 Diff. Threshold", value=f"`{blockData[3]}`", inline=False)
            embed.add_field(name="⌛ Block Creation Time", value=f"<t:{blockData[4]}:f>", inline=False)
            embed.add_field(name="⏲️ Block Creation Time Unix", value=f"`{blockData[4]}`", inline=False)
            return embed
        else: return self.bot.error_embed("This block does not exist!") # Error embed if block doesn't exist

async def setup(bot):
    await bot.add_cog(Blocks(bot))