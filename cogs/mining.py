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

class Mining(commands.Cog):
    """
    ## Mining commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['m', 'M'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.user)
    async def mine(self, ctx):
        user_data = self.bot.database.get_user(ctx.author.id)
        user_automine_status = self.bot.database.get_auto_miner(ctx.author.id)
        curr_block = self.bot.database.get_current_block()
        
        # Check if user is automining
        if user_data is not None and user_automine_status is not None:
            # Automine embed
            await ctx.reply(embed=self.autominer_embed(curr_block, user_automine_status))

        # First, check if the user exists
        elif user_data is not None:
            # Run the mine function to recieve results of mining
            guess, reciept = self.bot.database.mine(ctx.author.id)

            # If the guess was unsuccessful - womp womp
            if reciept is None:
                # Pool share submission
                if user_data[4]==1:
                    embed=discord.Embed(title="Submitted share to pool!", description=f"Your contribution to block #{curr_block[0]}\nhas been logged to the pool!", color=EMB_COLOUR, timestamp=datetime.now())
                    embed.set_thumbnail(url=EMB_THUMBNAIL_LINK)
                    embed.add_field(name="✅ Shares You Submitted", value=f"`{self.bot.database.get_pool_miner(ctx.author.id)[2]}` Shares", inline=False)
                    embed.add_field(name="🌎 Global Shares Submitted", value=f"`{self.bot.database.get_pool_share_sum()[0]}` Shares", inline=False)
                    embed.add_field(name="💵 Estimated Reward", value=f"`{curr_block[1]*(self.bot.database.get_pool_miner(ctx.author.id)[2]/self.bot.database.get_pool_share_sum()[0]):.6f}` {DISPLAY_CURRENCY}", inline=False)
                # Solo attempt
                else:
                    embed=discord.Embed(title="Guess was unsuccessful!", description="Please try again!", color=EMB_COLOUR, timestamp=datetime.now())

            # If the guess was successful - payout
            else:
                # Congratulatory embed building
                embed=discord.Embed(title="You broke the block!", description="The rewards have been distributed!", color=EMB_COLOUR, timestamp=datetime.now())
                
                # Generates and sends an embed to dedicated channel and gets transaction IDs for usage
                ids = await self.block_broke_embed(user_data[0], reciept, curr_block)

                # For building embed
                if type(reciept) is list: # Pool payout
                    embed.add_field(name="🧾 Coinbase Transaction Reciept IDs", value=f"`{ids}`", inline=False)
                else: # Solo payout
                    embed.add_field(name="🧾 Coinbase Transaction Reciept ID", value=f"`{ids}` ", inline=False)

            # Shows the miner the guess they made and replies
            embed.add_field(name="⛏️ Your Guess", value=f"`{guess}`", inline=False)
            await ctx.reply(embed=embed)
        
        # If user doesn't exist, throw error embed/prompt to create
        else: await ctx.reply(embed=self.bot.error_embed(f"You do not have an account yet! Please run `{DEFAULT_PREFIX}create` to start."))
    
    def autominer_embed(self, curr_block, user_automine_status):
        # Generates autominer info embed
        embed=discord.Embed(title=f"You are automining block #{curr_block[0]}!", color=EMB_COLOUR, timestamp=datetime.now())
        embed.set_thumbnail(url=EMB_THUMBNAIL_LINK)
        embed.add_field(name="✅ Session Hashes", value=f"`{user_automine_status[2]}` Hashes")
        embed.add_field(name="⛏️ Session Blocks Broken", value=f"`{user_automine_status[1]}` Blocks")
        embed.add_field(name="💸 Session Payout", value=f"`{user_automine_status[3]}` {DISPLAY_CURRENCY}", inline=False)
        embed.add_field(name="⏱️ Session Start Time", value=f"<t:{user_automine_status[4]}:f>", inline=False)

        # Return built embed
        return embed
    
    def autominer_died_embed(self, user_automine_status):
        # Generates autominer info embed when the autominer dies (or is turned off)
        embed=discord.Embed(title=f"Your autominer has stopped!", description="Your autominer statistics:", color=EMB_COLOUR, timestamp=datetime.now())
        embed.set_thumbnail(url=EMB_THUMBNAIL_LINK)
        embed.add_field(name="✅ Total Hashes Submitted", value=f"`{user_automine_status[2]}` Hashes")
        embed.add_field(name="⛏️ Total Blocks Broken", value=f"`{user_automine_status[1]}` Blocks")
        embed.add_field(name="💸 End Session Payout", value=f"`{user_automine_status[3]}` {DISPLAY_CURRENCY}", inline=False)
        embed.add_field(name="⏱️ Automining Start Time", value=f"<t:{user_automine_status[4]}:f>", inline=False)

        return embed
    
    async def block_broke_embed(self, breaker_uuid, reciept, curr_block):
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
        channel = self.bot.get_channel(OUTPUT_CHANNEL)
        breaker = self.bot.database.get_user(breaker_uuid)
        channelEmbed=discord.Embed(title=f'🥳 Block #{curr_block[0]} Completed! 🥳', timestamp=datetime.now(), color=EMB_COLOUR)
        channelEmbed.add_field(name='Breaker', value=f'{breaker[5]} (`{breaker_uuid}`)', inline=False)
        if type(reciept) is list: channelEmbed.add_field(name='Transaction IDs', value=f'{ids}', inline=False)
        else: channelEmbed.add_field(name='Transaction IDs', value=f'{reciept[0]}', inline=False)
        await channel.send(embed=channelEmbed)

        # Returns transaction IDs
        return ids
    
    @commands.command(aliases=['pool', 'pl', 'pd'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.user)
    async def pool_data(self, ctx):
        user_data = self.bot.database.get_user(ctx.author.id)

        if user_data is not None:
            if user_data[4] == 1:
                currBlock = self.bot.database.get_current_block()
                embed=discord.Embed(title=f"Pool Statistics", description=f"These are the current pool\nstatistics for block #{currBlock[0]}.", color=EMB_COLOUR, timestamp=datetime.now())
                embed.set_thumbnail(url=EMB_THUMBNAIL_LINK)
                embed.add_field(name="✅ Shares You Submitted", value=f"`{self.bot.database.get_pool_miner(ctx.author.id)[2]}` Shares", inline=False)
                embed.add_field(name="🌎 Global Shares Submitted", value=f"`{self.bot.database.get_pool_share_sum()[0]}` Shares")
                if self.bot.database.get_pool_miner(ctx.author.id)[2] != 0:
                    embed.add_field(name="💵 Estimated Pool Reward", value=f"`{currBlock[1]*(self.bot.database.get_pool_miner(ctx.author.id)[2]/self.bot.database.get_pool_share_sum()[0]):.6f}` {DISPLAY_CURRENCY}", inline=False)
                await ctx.reply(embed=embed)
            else: await ctx.reply(embed=self.bot.error_embed(f"You aren't pool mining! Run `{DEFAULT_PREFIX}switch` to switch to pool mining."))
        else: await ctx.reply(embed=self.bot.error_embed(f"You do not have an account yet! Please run `{DEFAULT_PREFIX}create` to start."))
    
    @commands.command(aliases=['am', 'auto'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.user)
    async def automine(self, ctx):
        # Switches the user's mining status

        # Check if user exists
        if self.bot.database.get_user(ctx.author.id) is not None:
            user_automine_status = self.bot.database.get_auto_miner(ctx.author.id)
            result = self.bot.database.update_user_automining_status(ctx.author.id)
            if not result: 
                result="Manual"
                dead = self.autominer_died_embed(user_automine_status)
            else: result="Automining"
            embed=discord.Embed(title=f"You have switched to {result}!", color=EMB_COLOUR) # Replies to user of result
            await ctx.reply(embed=embed)

            try: await ctx.reply(embed=dead)
            except: pass
            
        else: await ctx.reply(embed=self.bot.error_embed(f"You do not have an account yet! Please run `{DEFAULT_PREFIX}create` to start.")) # If no account, prompt to create

    @commands.command()
    @commands.cooldown(1, COOLDOWN, commands.BucketType.user)
    async def switch(self, ctx):
        # Switches the user's pooling status

        # Check if user exists
        if self.bot.database.get_user(ctx.author.id) is not None:
            result = self.bot.database.update_user_pooling_status(ctx.author.id)
            embed=discord.Embed(title=f"You have switched to {result} Mining!", color=EMB_COLOUR) # Replies to user of result
            await ctx.reply(embed=embed)
        else: await ctx.reply(embed=self.bot.error_embed(f"You do not have an account yet! Please run `{DEFAULT_PREFIX}create` to start.")) # If no account, prompt to create

    async def autominer_broken():
        pass

async def setup(bot):
    await bot.add_cog(Mining(bot))