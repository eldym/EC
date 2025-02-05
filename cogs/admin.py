import discord
import asyncio

from discord.ext import commands

class Admin(commands.Cog):
    """
    ## Admin commands
    """

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['ab'])
    async def addBal(self, ctx, uuid, amount):
        # Adds balance to a specific user
        if ctx.author.id == self.bot.owner_id:
            print("ab run")
            """uuid = ''.join(uuid).strip('<@>')
            ecDataManip.updateUserBal(uuid, float(ecDataGet.getUser(uuid)[1]) + float(amount))
            await ctx.reply(f'Updated user funds by: {amount} {DISPLAY_CURRENCY}')"""

    @commands.command(aliases=['cu'])
    async def createUser(self, ctx, uuid):
        # Force creates a user to have a balance
        if ctx.author.id == self.bot.owner_id:
            """uuid = ''.join(uuid).strip('<@>')
            ecDataManip.createUser(uuid)
            await ctx.reply(f'Force created user balance.')"""

    @commands.command()
    async def kill(self, ctx):
        # Forces the bot to shut down, only use when a catastrophic bug arises!
        if ctx.author.id == self.bot.owner_id:
            """await ctx.reply("**FORCE SHUTDOWN?**\nPlease say \'yes\' or \'y\' within 15 seconds to complete this action.")
            def check(m):
                return (m.content.lower() == 'yes' or m.content.lower() == 'y') and m.channel == ctx.channel
            # Confirmation for the kill switch
            try: msg = await client.wait_for('message', check=check, timeout=15.0)
            except asyncio.TimeoutError: await ctx.reply("The action has been canceled.") # If timer runs out
            else: 
                exit()"""
            
async def setup(bot):
    await bot.add_cog(Admin(bot))