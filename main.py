import discord
import asyncio

from discord.ext import tasks, commands
from data import *
from plot import makePlot
from datetime import datetime
from config import PREFIXES, DEFAULT_PREFIX, CURRENCY, DISPLAY_CURRENCY, COOLDOWN, EMB_COLOUR, TOKEN, EC_THUMBNAIL_LINK, OUTPUT_CHANNEL, ADMIN_ID

client = commands.Bot(command_prefix = PREFIXES, intents=discord.Intents.all(), help_command=None)

@client.event
async def on_ready():
    # Starts up the bot!
    print('Waking up!')
    print('Starting status loop...')
    status.start()
    print('Starting automine loop...')
    run_automine.start()
    print(f"EC is online! :3\nLogged in as:\n\"{client.user}\"\nID: {client.user.id}")

@tasks.loop()
async def status():
    # Changes bot status every 20 seconds from status list
    statuses = [getUpToDateSupply(), "made w/ ❤️ by eld_!", f"EC difficulty: {ecDataGet.getCurrentBlock()[2]}", f"block #{ecDataGet.getCurrentBlock()[0]}"] # Add/edit status selection to your choosing

    # Loops through the statuses
    for status in statuses:
        await client.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = f"{status}"))
        await asyncio.sleep(20) # Time interval between changes in status (set to 20 seconds)

def getUpToDateSupply():
    # Tries to get supply and append, if fails just states 0 in supply
    try: supply = int(ecDataGet.getSupply()[0])
    except: return f"0 {CURRENCY} in supply"

    # Calculates if supply is large enough to shorten
    # Used modified solution originally by Adam Rosenfield (from: https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings)
    magnitude = 0
    while abs(supply) >= 1000:
        magnitude += 1
        supply /= 1000.0
    
    # If supply is sufficiently large enough to shorten (greater than 1000) will generate formatted string from divided supply num
    if magnitude >= 1: supStr = f"{supply:.2f}"
    else: supStr = supply # Otherwise, just proceed with original number

    return f"{supStr}{['', 'K', 'M', 'B', 'T'][magnitude]} {CURRENCY} in supply" # Creates the abbreviated form of number

@tasks.loop(seconds=10)
async def run_automine():
    # Time interval between mines set to 10 seconds

    # Automatically runs the mine command for users with automining on
    for i in ecDataGet.getAutoMiners():
        currBlock = ecDataGet.getCurrentBlock()
        guess, reciept = ecCore.mine(i[0])
        if reciept is None: pass
        else: 
            print('User ID:', i[0], 'broke the block. Guess was:', guess)
            await blockBrokeEmbed(i[0], reciept, currBlock)

@client.command()
@commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
async def create(ctx):
    if ecDataManip.createUser(ctx.author.id) is not False:
        await ctx.send(f"Congratulations! Your account has been made. Run `{DEFAULT_PREFIX}help` for more commands to continue!")
        await balance(ctx, str(ctx.author.id))
    else:
        await ctx.send(embed=errorEmbed("You already have an account!"))

@client.command(aliases=['b','bal','bank','wallet'])
@commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
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

            # Adds a description if the user is automining
            if ecDataGet.getAutoMiner(member.id) is None: autostatus = ''
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
            embed.add_field(name="☑️ Pooling", value=f"{"TRUE" if userData[4] == 1 else "FALSE"}", inline=False)
            embed.set_footer(text="Bot made with ❤️ by eld_!")
            await ctx.reply(embed=embed)
        else:
            if defaulted or member.id == ctx.author.id: 
                await create(ctx)
            else:
                await ctx.reply(embed=errorEmbed(f"Oop! Looks like {member.name} does not have an account!"))

# TRANSACTIONAL COMMANDS

@client.command(aliases=['p', 'pay', 'give'])
@commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
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
                    embed=discord.Embed(title="Transaction Success!", description=f"**{float(amount):.6f} {DISPLAY_CURRENCY}** was sent to **{reciever.name}**.", color=EMB_COLOUR, timestamp=datetime.now())
                    embed.add_field(name="🧾 Transaction ID", value=f"`{reciept[0]}`", inline=False)
                    embed.add_field(name="🛃 Fee", value=f"`{reciept[4]}` {DISPLAY_CURRENCY}", inline=False)
                    embed.set_footer(text=f"Currency sent by {ctx.author.name}!")
                    await ctx.reply(embed=embed)
                else:
                    # If there is an error, prints out error to user
                    await ctx.reply(f"`Error!`\n{reciept}")
        else: await ctx.reply(embed=errorEmbed("This user does not exist! Please check if you mentionned or typed their Discord ID correctly!"))
    else:
        # Reply error outs
        if senderData is None: await ctx.reply(embed=errorEmbed(f"You do not have an account yet! Please run `{DEFAULT_PREFIX}create` to start."))
        elif reciever == str(ctx.author.id): await ctx.reply(embed=errorEmbed("You can't send money to yourself!"))
        elif float(amount) < 0.000001: await ctx.reply(embed=errorEmbed(f"The amount you want to send must be greater than or equal to `0.000001` {DISPLAY_CURRENCY}!"))
        elif float(senderData[1]) < float(amount): await ctx.reply(embed=errorEmbed("Your balance is too low!"))
        else: await ctx.reply(embed=errorEmbed("**Nobody here but us chickens!**\nIf you found this error, please let eld know!"))

@client.command(aliases=['t', 'tran', 'log', 'reciept'])
@commands.cooldown(1, COOLDOWN, commands.BucketType.channel)

async def transaction(ctx, id):
    transaction = ecDataGet.getTransaction(id)

    # Checks if transaction exists
    if transaction is not None:
        # Embed building
        if transaction[1] != "Coinbase": sender = await ctx.bot.fetch_user(transaction[1])
        reciever = await ctx.bot.fetch_user(transaction[2])
        embed=discord.Embed(title=f"Transaction #{transaction[0]} Information", color=EMB_COLOUR)
        embed.set_thumbnail(url=EC_THUMBNAIL_LINK)
        if transaction[1] != "Coinbase": embed.add_field(name="📨 Sender", value=f"{sender.name} (`{transaction[1]}`)", inline=False)
        else: embed.add_field(name="📨 Sender", value=f"Coinbase", inline=False)
        embed.add_field(name="📥 Reciever", value=f"{reciever.name} (`{transaction[2]}`)", inline=False)
        embed.add_field(name="💵 Amount", value=f"`{transaction[3]}` {DISPLAY_CURRENCY}", inline=False)
        embed.add_field(name="🛃 Fee", value=f"`{transaction[4]}` {DISPLAY_CURRENCY}", inline=False)
        embed.add_field(name="⏱️ Time", value=f"<t:{transaction[5]}:f>", inline=False)
        embed.set_footer(text=f"Currency sent by {ctx.author.name}!")
        await ctx.reply(embed=embed)
    
    # If transaction doesn't exist, throw error embed
    else: await ctx.reply(embed=errorEmbed("This transaction does not exist!"))

@client.command(aliases=['s'])
@commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
async def supply(ctx):
    # Gives the user the supply of currency
    await ctx.reply(f"There is currently {ecDataGet.getSupply()[0]} {DISPLAY_CURRENCY} in supply.")

# MINING

@client.command(aliases=['m', 'M'])
@commands.cooldown(1, COOLDOWN, commands.BucketType.user)
async def mine(ctx):
    userData = ecDataGet.getUser(ctx.author.id)
    userAutomineStatus = ecDataGet.getAutoMiner(ctx.author.id)
    currBlock = ecDataGet.getCurrentBlock()
    
    # Check if user is automining
    if userData is not None and userAutomineStatus is not None:
        # Automine embed
        embed=discord.Embed(title=f"You are automining block #{currBlock[0]}!", description="*Note: You must disable automining to manually\ncontribute to breaking the block!*", color=EMB_COLOUR, timestamp=datetime.now())
        embed.set_thumbnail(url=EC_THUMBNAIL_LINK)
        embed.add_field(name="✅ Session Hashes", value=f"`{userAutomineStatus[2]}` Hashes")
        embed.add_field(name="⛏️ Session Blocks Broken", value=f"`{userAutomineStatus[1]}` Blocks")
        embed.add_field(name="💸 Session Payout", value=f"`{userAutomineStatus[3]}` {DISPLAY_CURRENCY}", inline=False)
        embed.add_field(name="⏱️ Session Start Time", value=f"<t:{userAutomineStatus[4]}:f>", inline=False)
        await ctx.reply(embed=embed)

    # First, check if the user exists
    elif userData is not None:
        # Run the mine function to recieve results of mining
        guess, reciept = ecCore.mine(ctx.author.id)

        # If the guess was unsuccessful - womp womp
        if reciept is None:
            # Pool share submission
            if userData[4]==1:
                embed=discord.Embed(title="Submitted share to pool!", description=f"Your contribution to block #{currBlock[0]}\nhas been logged to the pool!", color=EMB_COLOUR, timestamp=datetime.now())
                embed.set_thumbnail(url=EC_THUMBNAIL_LINK)
                embed.add_field(name="✅ Shares You Submitted", value=f"`{ecDataGet.getPoolMiner(ctx.author.id)[2]}` Shares", inline=False)
                embed.add_field(name="🌎 Global Shares Submitted", value=f"`{ecDataGet.getPoolShareSum()[0]}` Shares", inline=False)
                embed.add_field(name="💵 Estimated Reward", value=f"`{currBlock[1]*(ecDataGet.getPoolMiner(ctx.author.id)[2]/ecDataGet.getPoolShareSum()[0]):.6f}` {DISPLAY_CURRENCY}", inline=False)
            # Solo attempt
            else:
                embed=discord.Embed(title="Guess was unsuccessful!", description="Please try again!", color=EMB_COLOUR, timestamp=datetime.now())

        # If the guess was successful - payout
        else:
            # Congratulatory embed building
            embed=discord.Embed(title="You broke the block!", description="The rewards have been distributed!", color=EMB_COLOUR, timestamp=datetime.now())
            
            # Generates and sends an embed to dedicated channel and gets transaction IDs for usage
            ids = await blockBrokeEmbed(userData[0], reciept, currBlock)

            # For building embed
            if type(reciept) is list: # Pool payout
                embed.add_field(name="🧾 Coinbase Transaction Reciept IDs", value=f"`{ids}`", inline=False)
            else: # Solo payout
                embed.add_field(name="🧾 Coinbase Transaction Reciept ID", value=f"`{ids}` ", inline=False)

        # Shows the miner the guess they made and replies
        embed.add_field(name="⛏️ Your Guess", value=f"`{guess}`", inline=False)
        await ctx.reply(embed=embed)
    
    # If user doesn't exist, throw error embed/prompt to create
    else: await ctx.reply(embed=errorEmbed(f"You do not have an account yet! Please run `{DEFAULT_PREFIX}create` to start."))

@client.command(aliases=['pool', 'pl', 'pd'])
@commands.cooldown(1, COOLDOWN, commands.BucketType.user)
async def pool_data(ctx):
    userData = ecDataGet.getUser(ctx.author.id)

    if userData is not None:
        if userData[4] == 1:
            currBlock = ecDataGet.getCurrentBlock()
            embed=discord.Embed(title=f"Pool Statistics", description=f"These are the current pool\nstatistics for block #{currBlock[0]}.", color=EMB_COLOUR, timestamp=datetime.now())
            embed.set_thumbnail(url=EC_THUMBNAIL_LINK)
            embed.add_field(name="✅ Shares You Submitted", value=f"`{ecDataGet.getPoolMiner(ctx.author.id)[2]}` Shares", inline=False)
            embed.add_field(name="🌎 Global Shares Submitted", value=f"`{ecDataGet.getPoolShareSum()[0]}` Shares")
            if ecDataGet.getPoolMiner(ctx.author.id)[2] != 0:
                embed.add_field(name="💵 Estimated Pool Reward", value=f"`{currBlock[1]*(ecDataGet.getPoolMiner(ctx.author.id)[2]/ecDataGet.getPoolShareSum()[0]):.6f}` {DISPLAY_CURRENCY}", inline=False)
            await ctx.reply(embed=embed)
        else: await ctx.reply(embed=errorEmbed(f"You aren't pool mining! Run `{DEFAULT_PREFIX}switch` to switch to pool mining."))
    else: await ctx.reply(embed=errorEmbed(f"You do not have an account yet! Please run `{DEFAULT_PREFIX}create` to start."))

# MINE STATUS SWITCHING COMMANDS

@client.command(aliases=['am', 'auto'])
@commands.cooldown(1, COOLDOWN, commands.BucketType.user)
async def automine(ctx):
    # Switches the user's mining status

    # Check if user exists
    if ecDataGet.getUser(ctx.author.id) is not None:
        result = ecDataManip.updateUserAutominingStatus(ctx.author.id)
        if not result: result="Manual"
        else: result="Automining"
        embed=discord.Embed(title=f"You have switched to {result}!", color=EMB_COLOUR) # Replies to user of result
        await ctx.reply(embed=embed)
    else: await ctx.reply(embed=errorEmbed(f"You do not have an account yet! Please run `{DEFAULT_PREFIX}create` to start.")) # If no account, prompt to create

@client.command()
@commands.cooldown(1, COOLDOWN, commands.BucketType.user)
async def switch(ctx):
    # Switches the user's pooling status

    # Check if user exists
    if ecDataGet.getUser(ctx.author.id) is not None:
        result = ecDataManip.updateUserPoolingStatus(ctx.author.id)
        embed=discord.Embed(title=f"You have switched to {result} Mining!", color=EMB_COLOUR) # Replies to user of result
        await ctx.reply(embed=embed)
    else: await ctx.reply(embed=errorEmbed(f"You do not have an account yet! Please run `{DEFAULT_PREFIX}create` to start.")) # If no account, prompt to create

# BLOCK DATA COMMANDS

@client.command(aliases=['bi', 'blockinfo'])
@commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
async def block(ctx, blockNo):
    # Gives the user the block data
    block = ecDataGet.getBlock(blockNo)
    await ctx.reply(embed=blockEmbed(block))

@client.command(aliases=['cb', 'current', 'currentblock'])
@commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
async def current_block(ctx):
    # Gives the user the current block data
    curr = ecDataGet.getCurrentBlock()
    await ctx.reply(embed=blockEmbed(curr))

@client.command(aliases=['dp', 'diff'])
@commands.cooldown(1, 10, commands.BucketType.channel)
async def plot(ctx, *data_points):
    # Generates a plot of past block difficulties - default is 30
    defaulted = False

    # Checks if there is a given data points range
    if len(data_points) <= 0 or len(data_points) >= 2: # If no valid number is given
        data_points = 31
        defaulted = True
    elif type(data_points) is tuple: 
        data_points = int(data_points[0])
        if data_points > ecDataGet.getCurrentBlock()[0]: # Checks if range of data being requested would exceed how many blocks currently exist
            embed = errorEmbed("Cannot access block difficulty data that far!")
            data_points = None
    else: 
        embed = errorEmbed("Cannot access block difficulty data!")
        data_points = None

    if data_points is not None:
        difficulties_list = makePlot(data_points) # TODO: use difficulty list data for more statistics in this embed
        if defaulted: data_points -= 1

        embed = discord.Embed(title=f"Past {data_points} Blocks' Difficulty", description=f"A plot of past {data_points} blocks' (*not including current block*) difficulties:", color=EMB_COLOUR, timestamp=datetime.now()) #creates embed
        file = discord.File("chart.png", filename="image.png")
        embed.set_image(url="attachment://image.png")

        await ctx.reply(file=file, embed=embed)
    else: await ctx.reply(embed=embed)

# LEADERBOARD COMMAND

@client.command(aliases=['lb', 'leader', 'board'])
@commands.cooldown(1, 10, commands.BucketType.channel)
async def leaderboard(ctx, lbType, *page):
    # Gives the user leaderboards

    # Checks if it should default to page 1 (if there is no given page number or invalid input)
    if len(page) <= 0 or len(page) >= 2:
        page = 1
    elif type(page) is tuple:
        page = int(page[0])

    # Checks what the user inputs
    bOptions = ['b', 'bal', 'balance']
    sOptions = ['s', 'solo']
    pOptions = ['p', 'pool']

    data = None

    # Checks the typing of leaderboard requested
    if lbType.lower() in bOptions:
        lbType = 'Balance' # To send off to embed builder to specify
        data = ecDataGet.getBalancesDescending() # Gets database data
    elif lbType.lower() in sOptions:
        lbType = 'Solo Block'
        data = ecDataGet.getSoloBlockDescending()
    elif lbType.lower() in pOptions:
        lbType = 'Pool Block'
        data = ecDataGet.getPoolBlockDescending()
    
    # Replies built leaderboard embed
    if len(data) > 0 or data is None:
        embed = await lbEmbed(ctx, data, lbType, page)
        if embed is not None:
            await ctx.reply(embed=embed)
        else:
            await ctx.reply(embed = errorEmbed("**Nobody here but us chickens!**\nThere is no data to display!"))
    else:
        await ctx.reply(embed = errorEmbed("**Nobody here but us chickens!**\nThere is no data to display!"))

# EMBED BUILDING BELOW

async def blockBrokeEmbed(breakerUuid, reciept, currBlock):
    # Generates block broken embed
    ids = []
    # Pool payout
    if type(reciept) is list:
        i = 0
        while i < len(reciept):
            ids.append(reciept[i][0])
            i = i + 1
    # Solo payout
    else: ids = reciept[0]

    # Broadcasts to a channel that a block was broken
    channel = client.get_channel(OUTPUT_CHANNEL)
    breaker = await client.fetch_user(breakerUuid)
    channelEmbed=discord.Embed(title=f'🥳 Block #{currBlock[0]} Completed! 🥳', timestamp=datetime.now(), color=EMB_COLOUR)
    channelEmbed.add_field(name='Breaker', value=f'{breaker.name} (`{breakerUuid}`)', inline=False)
    if type(reciept) is list: channelEmbed.add_field(name='Transaction IDs', value=f'{ids}', inline=False)
    else: channelEmbed.add_field(name='Transaction IDs', value=f'{reciept[0]}', inline=False)
    await channel.send(embed=channelEmbed)

    # Returns transaction IDs
    return ids

def blockEmbed(blockData):
    # Generates block information embed if block exists
    if blockData is not None:
        embed=discord.Embed(title=f"Block #{blockData[0]} Information", description=f"{"*Current block!*" if blockData == ecDataGet.getCurrentBlock() else ""}", color=EMB_COLOUR)
        embed.set_thumbnail(url=EC_THUMBNAIL_LINK)
        embed.add_field(name="💵 Reward Amount", value=f"`{blockData[1]:.6f}` {DISPLAY_CURRENCY}", inline=False)
        embed.add_field(name="⚒️ Difficulty", value=f"`{blockData[2]}`", inline=False)
        if blockData == ecDataGet.getCurrentBlock(): embed.add_field(name="🌎 Current Pool Effort", value=f"{ecDataGet.getPoolShareSum()[0]} Shares", inline=False)
        embed.add_field(name="📊 Diff. Threshold", value=f"`{blockData[3]}`", inline=False)
        embed.add_field(name="⌛ Block Creation Time", value=f"<t:{blockData[4]}:f>", inline=False)
        embed.add_field(name="⏲️ Block Creation Time Unix", value=f"`{blockData[4]}`", inline=False)
        return embed
    else: return errorEmbed("This block does not exist!") # Error embed if block doesn't exist

async def lbEmbed(ctx, data, lbType, page):
    # Generates leaderboard embeds

    # Calculates index ranges from given page number
    if type(page) is int and page >= 1: 
        startIndex = (page*10) - 10
        endIndex = (page*10)
    else: 
        startIndex = 0
        endIndex = 10
    
    # Gets the users between the index points
    lbData = data[startIndex:endIndex]

    # If there is results from the given page number
    if len(lbData) >= 1:
        # Determines whether it should be displaying the currency or blocks for lb building
        if lbType == "Balance": 
            whichType = DISPLAY_CURRENCY
            whichNumber = 1 # to display currency
        else: 
            whichType = "block(s)"
            if lbType == "Pool Block":
                whichNumber = 2 # to display pool
            else:
                whichNumber = 3 # to display solo

        # Building embed
        embed = discord.Embed(title=f"{lbType} Leaderboard", color=EMB_COLOUR, timestamp=datetime.now())
        startIndex += 1
        for i in lbData:
            user = await ctx.bot.fetch_user(i[0])
            embed.add_field(name=f"{startIndex}. {user.name.replace('_', '\\_')} (`{i[0]}`)", value=f"{i[whichNumber]} {whichType}", inline=False)
            startIndex += 1
        
        # Shows page number
        embed.set_footer(text=f"Page {page}")

        # Returns final leaderboard embed
        return embed
    else:
        return None # If there are no results, send None

def errorEmbed(errorMsg):
    # Generates the error message embed with a given descriptor
    return discord.Embed(title=f"Error!", description=f"{errorMsg}", color=EMB_COLOUR, timestamp=datetime.now())

# ADMIN COMMANDS

@client.command(aliases=['ab'])
@commands.cooldown(1, 2, commands.BucketType.channel)
async def addBal(ctx, uuid, amount):
    # Adds balance to a specific user
    if ctx.author.id == ADMIN_ID:
        uuid = ''.join(uuid).strip('<@>')
        ecDataManip.updateUserBal(uuid, float(ecDataGet.getUser(uuid)[1]) + float(amount))
        await ctx.reply(f'Updated user funds by: {amount} {DISPLAY_CURRENCY}')

@client.command(aliases=['cu'])
@commands.cooldown(1, 2, commands.BucketType.channel)
async def createUser(ctx, uuid):
    # Force creates a user to have a balance
    if ctx.author.id == ADMIN_ID:
        uuid = ''.join(uuid).strip('<@>')
        ecDataManip.createUser(uuid)
        await ctx.reply(f'Force created user balance.')

@client.command()
@commands.cooldown(1, 2, commands.BucketType.channel)
async def kill(ctx):
    # Forces the bot to shut down, only use when a catastrophic bug arises!
    if ctx.author.id == ADMIN_ID:
        await ctx.reply("**FORCE SHUTDOWN?**\nPlease say \'yes\' or \'y\' within 15 seconds to complete this action.")
        def check(m):
            return (m.content.lower() == 'yes' or m.content.lower() == 'y') and m.channel == ctx.channel
        # Confirmation for the kill switch
        try: msg = await client.wait_for('message', check=check, timeout=15.0)
        except asyncio.TimeoutError: await ctx.reply("The action has been canceled.") # If timer runs out
        else: 
            exit()

client.run(TOKEN)