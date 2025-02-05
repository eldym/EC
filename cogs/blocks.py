import discord
import asyncio
import json

from discord.ext import commands
from datetime import datetime

def get_config():
    with open('config.json') as f:
        return json.load(f)

config = get_config()

COOLDOWN = config["cooldown"]
EMB_COLOUR = 0x000000
DEFAULT_PREFIX = config["prefixes"][0]
DISPLAY_CURRENCY = config["display_currency"]
OUTPUT_CHANNEL = config["output_channel_id"]
EMB_THUMBNAIL_LINK = config["emb_thumbnail_link"]

class Blocks(commands.Cog):
    """
    ## Block commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['bi', 'blockinfo'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def block(self, ctx, blockNo):
        # Gives the user the block data
        block = self.bot.database.get_block(blockNo)
        await ctx.reply(embed=self.block_embed(block))

    @commands.command(aliases=['cb', 'current', 'currentblock'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def current_block(self, ctx):
        # Gives the user the current block data
        curr = self.bot.database.get_current_block()
        await ctx.reply(embed=self.block_embed(curr))

    def block_embed(self, blockData):
    # Generates block information embed if block exists
        if blockData is not None:
            embed=discord.Embed(title=f"Block #{blockData[0]} Information", description=f"{"*Current block!*" if blockData == self.bot.database.get_current_block() else ""}", color=EMB_COLOUR)
            embed.set_thumbnail(url=EMB_THUMBNAIL_LINK)
            embed.add_field(name="💵 Reward Amount", value=f"`{blockData[1]:.6f}` {DISPLAY_CURRENCY}", inline=False)
            embed.add_field(name="⚒️ Difficulty", value=f"`{blockData[2]}`", inline=False)
            if blockData == self.bot.database.get_current_block(): embed.add_field(name="🌎 Current Pool Effort", value=f"{self.bot.database.get_pool_share_sum()[0]} Shares", inline=False)
            embed.add_field(name="📊 Diff. Threshold", value=f"`{blockData[3]}`", inline=False)
            embed.add_field(name="⌛ Block Creation Time", value=f"<t:{blockData[4]}:f>", inline=False)
            embed.add_field(name="⏲️ Block Creation Time Unix", value=f"`{blockData[4]}`", inline=False)
            return embed
        else: return self.bot.error_embed("This block does not exist!") # Error embed if block doesn't exist

async def setup(bot):
    await bot.add_cog(Blocks(bot))