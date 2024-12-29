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

@client.command()
@commands.cooldown(1, 2, commands.BucketType.guild)
async def create(ctx):
    if ecDataManip.createUser(ctx.author.id) is not False:
        await ctx.send(f"Congratulations! Your account has been made. Run `{DEFAULT_PREFIX}help` for more commands to continue!")
        await balance(ctx, str(ctx.author.id))
    else:
        await ctx.send("`Error!`\nYou already have an account!")

# @client.hybrid_command()
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
            except: embed.set_thumbnail(url=f'https://cdn.discordapp.com/embed/avatars/{random.randint(0,5)}.png')    
            embed.add_field(name="💵 Currency", value=f"{userData[1]} {CURRENCY}", inline=False)
            embed.add_field(name="☑️ Pool Blocks", value=f"{userData[2]:,} block{bGrammar1} broken", inline=False)
            embed.add_field(name="☑️ Solo Blocks", value=f"{userData[3]:,} block{bGrammar2} broken", inline=False)
            embed.set_footer(text="Bot made with ❤️ by eld_!")
            await ctx.reply(embed=embed)
        else:
            if defaulted or member.id == ctx.author.id: 
                await create(ctx)
            else:
                await ctx.reply(f"`Error!`\nOop! Looks like {member.name} does not have an account!")


# @client.hybrid_command()
@client.command(aliases=['pay', 'give'])
@commands.cooldown(1, 2, commands.BucketType.guild)
async def send(ctx, reciever, amount):
    senderData = ecDataGet.getUser(ctx.author.id)
    reciever = ''.join(reciever).strip('<@>')
    recieverData = ecDataGet.getUser(reciever)

    if senderData is not None and reciever != str(ctx.author.id) and float(amount) >= 0.000001 and float(senderData[1]) >= float(amount):
        if recieverData is not None:
            # Confirmation
            await ctx.reply("Please say \'yes\' or \'y\' within 30 seconds to complete this transaction.")
            def check(m):
                return (m.content.lower() == 'yes' or m.content.lower() == 'y') and m.channel == ctx.channel
            # Timed confirmation
            try: msg = await client.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError: await ctx.reply("The transaction has been canceled.") # If timer runs out
            else: # If confirmation is made
                reciept = ecCore.transaction(ctx.author.id, reciever, amount)
                if type(reciept) is tuple:
                    # Gets the reciever as a User object
                    reciever = await ctx.bot.fetch_user(reciever)

                    # Embed building
                    embed=discord.Embed(title="Transaction Success!", description=f"**{float(amount):.6f} {CURRENCY}** was sent to **{reciever.name}**.", color=EMB_COLOUR, timestamp=datetime.now())
                    embed.add_field(name="Transaction ID", value=f"`{reciept[0]}`", inline=False)
                    embed.add_field(name="Fee", value=f"`{reciept[4]}` {CURRENCY}", inline=False)
                    embed.set_footer(text=f"Currency sent by {ctx.author.name}!")
                    await ctx.reply(embed=embed)
                else:
                    # If there is an error, prints out error to user
                    await ctx.reply(f"`Error!`\n{reciept}")
        else: ctx.reply(f"`Error!`\nThis user does not exist! Please check if you mentionned or typed their Discord ID correctly!")
    else:
        if senderData is None: await ctx.reply(f"`Error!`\nYou do not have an account yet! Please run `!create` to start.")
        elif reciever == str(ctx.author.id): await ctx.reply(f"`Error!`\nYou can't send money to yourself!")
        elif float(amount) < 0.000001: await ctx.reply(f"`Error!`\nThe amount you want to send must be greater than or equal to `0.000001` {CURRENCY}!")
        elif float(senderData[1]) < float(amount): await ctx.reply(f"`Error!`\nYour balance is too low!")
        else: await ctx.reply(f"`Error!`\n**Nobody here but us chickens!** If you found this error, please let eld know!")

@client.command()
@commands.cooldown(1, 2, commands.BucketType.guild)
async def createMoney(ctx, amount):
    if ctx.author.id == 395368734732189696:
        ecDataManip.updateUserBal(ctx.author.id, amount)
        await ctx.reply(f'generated {amount} funds')

@client.command()
@commands.cooldown(1, 2, commands.BucketType.guild)
async def createUser(ctx, uuid):
    if ctx.author.id == 395368734732189696:
        uuid = ''.join(uuid).strip('<@>')
        ecDataManip.createUser(uuid)
        await ctx.reply(f'force created user balance')

client.run(TOKEN)