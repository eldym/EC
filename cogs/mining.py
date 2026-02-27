import discord
from discord.ext import commands
from datetime import datetime

COOLDOWN = 2
EMB_COLOUR = 0x000000

class Mining(commands.Cog):
    """
    Mining commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.default_prefix = bot.config["prefixes"][0]
        self.display_currency = bot.config["display_currency"]
        self.output_channel = bot.config["output_channel_id"]
        self.emb_thumbnail_link = bot.config["emb_thumbnail_link"]

    @commands.command(aliases=['m', 'M'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.user)
    async def mine(self, ctx):
        """Runs a random guess between 0 - current difficulty. If guess is less than difficulty threshold, the block breaks and rewards the breaker."""
        user_data = self.bot.database.get_user(ctx.author.id)
        curr_block = self.bot.database.get_current_block()
        
        # First, check if the user exists
        if user_data is not None:
            # Run the mine function to recieve results of mining
            guess, reciept = self.bot.database.mine(ctx.author.id)

            # If the guess was unsuccessful - womp womp
            if reciept is None:
                # Pool share submission
                if user_data[3]==1:
                    embed=discord.Embed(title="Submitted share of work to pool!", description=f"Your contribution to block #{curr_block[0]}\nhas been logged to the pool!", color=EMB_COLOUR, timestamp=datetime.now())
                    embed.set_thumbnail(url=self.emb_thumbnail_link)
                    embed.add_field(name="✅ Shares You Submitted", value=f"`{self.bot.database.get_pool_miner(ctx.author.id)[2]}` Shares", inline=False)
                    embed.add_field(name="🌎 Global Shares Submitted", value=f"`{self.bot.database.get_pool_share_sum()[0]}` Shares", inline=False)
                    embed.add_field(name="💵 Estimated Reward", value=f"`{curr_block[1]*(self.bot.database.get_pool_miner(ctx.author.id)[2]/self.bot.database.get_pool_share_sum()[0]):.6f}` {self.display_currency}", inline=False)
                # Solo attempt
                else:
                    embed=discord.Embed(title="Guess was unsuccessful!", description="Please try again!", color=EMB_COLOUR, timestamp=datetime.now())

            # If the guess was successful - payout
            else:
                # Congratulatory embed building
                embed=discord.Embed(title="You broke the block!", description="The rewards have been distributed!", color=EMB_COLOUR, timestamp=datetime.now())
                
                # Generates and sends an embed to dedicated channel and gets transaction IDs for usage
                ids = await self.block_broke_embed(user_data, reciept, curr_block)

                # For building embed
                embed.add_field(name=f"🧾 Coinbase Transaction Reciept ID{'s' if type(reciept) is list else ""}", value=f"`{ids}`", inline=False)

            # Shows the miner the guess they made and replies
            embed.add_field(name="⛏️ Your Guess", value=f"`{guess}`", inline=False)
            await ctx.reply(embed=embed)
        
        # If user doesn't exist, throw error embed/prompt to create
        else: await ctx.reply(embed=self.bot.noacc())
    
    async def block_broke_embed(self, user_data, reciept, curr_block):
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

        uuid = user_data[0]
        username = user_data[4]

        # Broadcasts to a channel that a block was broken
        channel = self.bot.get_channel(self.output_channel)
        channelEmbed=discord.Embed(title=f'🥳 Block #{curr_block[0]} Broke! 🥳', timestamp=datetime.now(), color=EMB_COLOUR)
        channelEmbed.add_field(name='Breaker', value=f'{username} (`{uuid}`)', inline=False)
        if type(reciept) is list: channelEmbed.add_field(name='Transaction IDs', value=f'{ids}', inline=False)
        else: channelEmbed.add_field(name='Transaction IDs', value=f'{reciept[0]}', inline=False)
        await channel.send(embed=channelEmbed)

        # Returns transaction IDs
        return ids
    
    @commands.command(aliases=['pool', 'pl', 'pd'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.user)
    async def pool_data(self, ctx):
        """Displays current pool data."""
        user_data = self.bot.database.get_user(ctx.author.id)

        if user_data is not None:
            if user_data[4] == 1:
                currBlock = self.bot.database.get_current_block()
                embed=discord.Embed(title=f"Pool Statistics", description=f"These are the current pool\nstatistics for block #{currBlock[0]}.", color=EMB_COLOUR, timestamp=datetime.now())
                embed.set_thumbnail(url=self.emb_thumbnail_link)
                embed.add_field(name="✅ Shares You Submitted", value=f"`{self.bot.database.get_pool_miner(ctx.author.id)[2]}` Shares", inline=False)
                embed.add_field(name="🌎 Global Shares Submitted", value=f"`{self.bot.database.get_pool_share_sum()[0]}` Shares")
                if self.bot.database.get_pool_miner(ctx.author.id)[2] != 0:
                    embed.add_field(name="💵 Estimated Pool Reward", value=f"`{currBlock[1]*(self.bot.database.get_pool_miner(ctx.author.id)[2]/self.bot.database.get_pool_share_sum()[0]):.6f}` {self.display_currency}", inline=False)
                await ctx.reply(embed=embed)
            else: await ctx.reply(embed=self.bot.error_embed(f"You aren't pool mining! Run `{self.default_prefix}switch` to switch to pool mining."))
        else: await ctx.reply(embed=self.bot.error_noacc())

    @commands.command()
    @commands.cooldown(1, COOLDOWN, commands.BucketType.user)
    async def switch(self, ctx):
        """Switches user pooling status."""
        # Check if user exists
        if self.bot.database.get_user(ctx.author.id) is not None:
            result = self.bot.database.update_user_pooling_status(ctx.author.id)
            embed=discord.Embed(title=f"You have switched to {result} Mining!", color=EMB_COLOUR) # Replies to user of result
            await ctx.reply(embed=embed)
        else: await ctx.reply(embed=self.bot.error_noacc())

async def setup(bot):
    await bot.add_cog(Mining(bot))