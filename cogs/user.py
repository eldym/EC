import discord
import asyncio
import json
import random

from discord.ext import commands
from datetime import datetime

def get_config():
    with open('config.json') as f:
        return json.load(f)

config = get_config()

EMB_COLOUR = 0x000000
COOLDOWN = config["cooldown"]
DEFAULT_PREFIX = config["prefixes"][0]
DISPLAY_CURRENCY = config["display_currency"]

class User(commands.Cog):
    """
    ## User commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def create(self, ctx):
        if self.bot.database.create_user(ctx.author.id) is not False:
            await ctx.send(f"Congratulations! Your account has been made. Run `{DEFAULT_PREFIX}help` for more commands to continue!")
            await self.balance(ctx, str(ctx.author.id))
        else:
            await ctx.send(embed=self.bot.error_embed("You already have an account!"))
    
    @commands.command(aliases=['b','bal','bank','wallet'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def balance(self, ctx, *member):
        member = ''.join(member).strip('<@>')
        defaulted = False

        try: member = await ctx.bot.fetch_user(member)
        except: member = ctx.author; defaulted = True
        finally:
            userData = self.bot.database.get_user(member.id)

            if userData is not None:
                # Block or blocks?
                if userData[2] != 1: bGrammar1 = 's'
                else: bGrammar1 = ''
                if userData[3] != 1: bGrammar2 = 's'
                else: bGrammar2 = ''

                # Defaults to author's if member mentionned couldn't be found
                if defaulted or member.id == ctx.author.id: embTitle = "Your Balance"
                else: embTitle = f"{member.name}\'s Balance"

                # Adds a description if the user is automining
                if self.bot.database.get_auto_miner(member.id) is None: autostatus = ''
                else:
                    if member.id == ctx.author.id: autostatus = '*You are currently automining.*'
                    else: autostatus = "*This user is currently automining.*"

                # Embed building
                embed=discord.Embed(title=embTitle, description=f"{autostatus}", color=EMB_COLOUR, timestamp=datetime.now())
                try: embed.set_thumbnail(url=member.avatar.url)
                except: embed.set_thumbnail(url=f'https://cdn.discordapp.com/embed/avatars/{random.randint(0,5)}.png')    
                embed.add_field(name="💵 Currency", value=f"{userData[1]} {DISPLAY_CURRENCY}", inline=False)
                embed.add_field(name="☑️ Pool Blocks", value=f"{userData[2]:,} block{bGrammar1} broken", inline=False)
                embed.add_field(name="☑️ Solo Blocks", value=f"{userData[3]:,} block{bGrammar2} broken", inline=False)
                embed.add_field(name="🚤 Pooling", value=f"{"TRUE" if userData[4] == 1 else "FALSE"}", inline=False)
                embed.set_footer(text="Bot made with ❤️ by eld_!")
                await ctx.reply(embed=embed)
            else:
                if defaulted or member.id == ctx.author.id: 
                    await self.create(ctx)
                else:
                    await ctx.reply(embed=self.bot.error_embed(f"{member.name} does not have an account!"))


async def setup(bot):
    await bot.add_cog(User(bot))