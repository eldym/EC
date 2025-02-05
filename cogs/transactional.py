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
EMB_THUMBNAIL_LINK = config["emb_thumbnail_link"]

class Transactional(commands.Cog):
    """
    ## Transaction commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['p', 'pay', 'give'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def send(self, ctx, reciever, amount):
        senderData = self.bot.database.get_user(ctx.author.id)
        reciever = ''.join(reciever).strip('<@>')
        recieverData = self.bot.database.get_user(reciever)

        if senderData is not None and reciever != str(ctx.author.id) and float(amount) >= 0.000001 and float(senderData[1]) >= float(amount):
            if recieverData is not None:
                # Confirmation
                await ctx.reply("Please say \'yes\' or \'y\' within 30 seconds to complete this transaction.")
                def check(m):
                    return (m.content.lower() == 'yes' or m.content.lower() == 'y') and m.channel == ctx.channel
                # Timed confirmation
                try: msg = await self.bot.wait_for('message', check=check, timeout=30.0)
                except asyncio.TimeoutError: await ctx.reply("The transaction has been canceled.") # If timer runs out
                else: # If confirmation is made
                    reciept = self.bot.database.transaction(ctx.author.id, reciever, amount)
                    if type(reciept) is tuple:
                        # Gets the reciever as a User object
                        reciever = await ctx.bot.fetch_user(reciever)

                        # Embed building
                        embed=discord.Embed(title="Transaction Success!", description=f"**{float(amount):.6f} {DISPLAY_CURRENCY}** was sent to **{reciever.name}**.", color=EMB_COLOUR, timestamp=datetime.now())
                        embed.add_field(name="🧾 Transaction ID", value=f"`{reciept[0]}`", inline=False)
                        embed.add_field(name="🛃 Fee", value=f"`{reciept[4]}` {DISPLAY_CURRENCY}", inline=False)
                        embed.set_footer(text=f"Currency sent by {ctx.author.name}!")
                        await ctx.reply(embed=embed)
                    else:
                        # If there is an error, prints out error to user
                        await ctx.reply(f"`Error!`\n{reciept}")
            else: await ctx.reply(embed=self.bot.error_embed("This user does not exist! Please check if you mentionned or typed their Discord ID correctly!"))
        else:
            # Reply error outs
            if senderData is None: await ctx.reply(embed=self.bot.error_embed(f"You do not have an account yet! Please run `{DEFAULT_PREFIX}create` to start."))
            elif reciever == str(ctx.author.id): await ctx.reply(embed=self.bot.error_embed("You can't send money to yourself!"))
            elif float(amount) < 0.000001: await ctx.reply(embed=self.bot.error_embed(f"The amount you want to send must be greater than or equal to `0.000001` {DISPLAY_CURRENCY}!"))
            elif float(senderData[1]) < float(amount): await ctx.reply(embed=self.bot.error_embed("Your balance is too low!"))
            else: await ctx.reply(embed=self.bot.error_embed("**Nobody here but us chickens!**\nIf you found this error, please let eld know!"))

    @commands.command(aliases=['t', 'tran', 'log', 'reciept'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def transaction(self, ctx, id):
        transaction = self.bot.database.get_transaction(id)

        # Checks if transaction exists
        if transaction is not None:
            # Embed building
            if transaction[1] != "Coinbase": sender = await ctx.bot.fetch_user(transaction[1])
            reciever = await ctx.bot.fetch_user(transaction[2])
            embed=discord.Embed(title=f"Transaction #{transaction[0]} Information", color=EMB_COLOUR)
            embed.set_thumbnail(url=EMB_THUMBNAIL_LINK)
            if transaction[1] != "Coinbase": embed.add_field(name="📨 Sender", value=f"{sender.name} (`{transaction[1]}`)", inline=False)
            else: embed.add_field(name="📨 Sender", value=f"Coinbase", inline=False)
            embed.add_field(name="📥 Reciever", value=f"{reciever.name} (`{transaction[2]}`)", inline=False)
            embed.add_field(name="💵 Amount", value=f"`{transaction[3]}` {DISPLAY_CURRENCY}", inline=False)
            embed.add_field(name="🛃 Fee", value=f"`{transaction[4]}` {DISPLAY_CURRENCY}", inline=False)
            embed.add_field(name="⏱️ Time", value=f"<t:{transaction[5]}:f>", inline=False)
            embed.set_footer(text=f"Currency sent by {ctx.author.name}!")
            await ctx.reply(embed=embed)
        
        # If transaction doesn't exist, throw error embed
        else: await ctx.reply(embed=self.bot.error_embed("This transaction does not exist!"))

async def setup(bot):
    await bot.add_cog(Transactional(bot))