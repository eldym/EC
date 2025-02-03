import discord
import asyncio
import json

from discord.ext import commands

def get_config():
    with open('config.json') as f:
        return json.load(f)

config = get_config()

class admin(commands.Cog):
    """
    Admin commands
    """

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['ab'])
    async def addBal(ctx, uuid, amount):
        # Adds balance to a specific user
        if ctx.author.id == config["admin_id"]:
            """uuid = ''.join(uuid).strip('<@>')
            ecDataManip.updateUserBal(uuid, float(ecDataGet.getUser(uuid)[1]) + float(amount))
            await ctx.reply(f'Updated user funds by: {amount} {DISPLAY_CURRENCY}')"""