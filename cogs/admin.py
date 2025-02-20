import discord
import asyncio
import json

from discord.ext import commands

def get_config():
    with open('config.json') as f:
        return json.load(f)

config = get_config()

DISPLAY_CURRENCY = config["display_currency"]

class Admin(commands.Cog):
    """
    ## Admin commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.reply(f"**Latency:** `{self.bot.latency*1000} ms`")
    
    @commands.command(aliases=['ab'])
    async def add_to_bal(self, ctx, uuid, amount):
        # Adds balance to a specific user
        if ctx.author.id == self.bot.owner_id:
            uuid = ''.join(uuid).strip('<@>')
            self.bot.database.update_user_bal(uuid, float(self.bot.database.get_user(uuid)[1]) + float(amount))
            await ctx.reply(f'Updated user funds by: {amount} {DISPLAY_CURRENCY}')

    @commands.command(aliases=['cu'])
    async def create_user(self, ctx, uuid):
        # Force creates a user to have a balance
        if ctx.author.id == self.bot.owner_id:
            uuid = ''.join(uuid).strip('<@>')
            self.bot.database.create_user(uuid)
            await ctx.reply(f'Forced user balance creation.')

    @commands.command(aliases=['uu'])
    async def update_usernames(self, ctx):
        # Force creates a user to have a balance
        if ctx.author.id == self.bot.owner_id:
            list_of_users = self.bot.database.get_all_users()
            for user in list_of_users:
                fetched_user = await ctx.bot.fetch_user(user[0])

                if user[5] != fetched_user.name:
                    self.bot.database.update_username(user[0], fetched_user.name)
                    print(f"Updated username in database: {user[5]} -> {fetched_user.name}")
                else: print("its fine")

            await ctx.reply(f'Updated all usernames where applicable.')

    # DANGER ZONE

    @commands.command()
    async def kill(self, ctx):
        # Forces the bot to shut down, only use when a catastrophic bug arises!
        if ctx.author.id == self.bot.owner_id:
            await ctx.reply("**FORCE SHUTDOWN?**\nPlease say \'yes\' or \'y\' within 15 seconds to complete this action.")
            def check(m):
                return (m.content.lower() == 'yes' or m.content.lower() == 'y') and m.channel == ctx.channel
            # Confirmation for the kill switch
            try: msg = await self.bot.wait_for('message', check=check, timeout=15.0)
            except asyncio.TimeoutError: await ctx.reply("The action has been canceled.") # If timer runs out
            else: 
                exit()
            
async def setup(bot):
    await bot.add_cog(Admin(bot))