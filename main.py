import discord
import asyncio

from discord.ext import tasks, commands
from data import *
from datetime import datetime
from config import PREFIXES, DEFAULT_PREFIX, CURRENCY, COOLDOWN, EMB_COLOUR, TOKEN

client = commands.Bot(command_prefix = PREFIXES , intents=discord.Intents.all(), help_command=None)

@client.event
async def on_ready():
    # TODO: Make a changing status
    print(f"EC is online! :3\nLogged in as:\n\"{client.user}\"\nID: {client.user.id}")
    # Startup
    ecDatabaseCreate.sqlDBCreate()
    ecDatabaseCreate.sqlTablesCreate()

@client.command()
@commands.cooldown(1, 2, commands.BucketType.guild)
async def create(ctx):
    if ecDataManip.createUser(ctx.author.id) is not False:
        await ctx.send(f"Congratulations! Your account has been made. Run `{DEFAULT_PREFIX}help` for more commands to continue!")
        balance(ctx, ctx.author.id)
    else:
        await ctx.send("`Error!`\nYou already have an account!")

@client.command(aliases=['b','bal','bank','wallet'])
@commands.cooldown(1, 2, commands.BucketType.guild)
async def balance(ctx, *member):
    member = ''.join(member).strip('<@>')
    defaulted = False

    try: member = await ctx.bot.fetch_user(member)
    except: member = ctx.author; defaulted = True
    finally:
        userData = ecDataGet.getUser(member.id)

        if userData is not None:
            # Block or blocks?
            if userData[2] != 1: bGrammar1 = 's'
            else: bGrammar1 = ''
            if userData[3] != 1: bGrammar2 = 's'
            else: bGrammar2 = ''

            # Defaults to author's if member mentionned couldn't be found
            if defaulted or member.id == ctx.author.id: embTitle = "Your Balance"
            else: embTitle = f"{member.name}\'s Balance"

            # Embed building
            embed=discord.Embed(title=embTitle, color=EMB_COLOUR, timestamp=datetime.now())
            try: embed.set_thumbnail(url=member.avatar.url)
            except: embed.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')    
            embed.add_field(name="💵 Currency", value=f"{userData[1]} {CURRENCY}", inline=False)
            embed.add_field(name="☑️ Pool Blocks", value=f"{userData[2]:,} block{bGrammar1} broken", inline=False)
            embed.add_field(name="☑️ Solo Blocks", value=f"{userData[3]:,} block{bGrammar2} broken", inline=False)
            embed.set_footer(text="Bot made with ❤️ by eld_!")
            await ctx.send(embed=embed)
        else:
            if defaulted or member.id == ctx.author.id: 
                create(ctx)
            else:
                await ctx.send(f"`Error!`\nOop! Looks like {member.name} does not have an account!")


client.run(TOKEN)