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
        curr_block = self.bot.database.get_current_block_relevant_md()

        # Check if user exists
        if user_data is None:
            await ctx.reply(embed=self.bot.error_noacc())
            return
        
        # Check if user is automining
        user_automine_status = self.bot.database.get_auto_miner(ctx.author.id)
        if user_automine_status is not None:
            # Redirect to automine embed
            await ctx.reply(embed=self.autominer_embed(curr_block, user_automine_status))
            return
        
        # Otherwise, run the mine function to recieve results of mining
        guess, reciept = self.bot.database.mine(ctx.author.id)

        # If the guess was unsuccessful - womp womp
        if reciept is None:
            # Pool share submission
            if user_data[3]==1:
                share_sum = self.bot.database.get_pool_share_sum()[0]
                user_pool_shares = self.bot.database.get_pool_miner(ctx.author.id)[2]

                embed=discord.Embed(title="Submitted share of work to pool!", description=f"Your contribution to block #{curr_block[0]}\nhas been logged!", color=EMB_COLOUR, timestamp=datetime.now())
                embed.set_thumbnail(url=self.emb_thumbnail_link)
                embed.add_field(name="✅ Shares You Submitted", value=f"`{user_pool_shares}` Shares", inline=False)
                embed.add_field(name="🌎 Global Shares Submitted", value=f"`{share_sum}` Shares", inline=False)
                embed.add_field(name="💵 Estimated Reward", value=f"`{curr_block[1]*(user_pool_shares/share_sum):.6f}` {self.display_currency}", inline=False)
            # Solo attempt
            else:
                embed=discord.Embed(title="Guess was unsuccessful!", description="Please try again!", color=EMB_COLOUR, timestamp=datetime.now())

        # If the guess was successful - payout!
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

    @commands.command(aliases=['am', 'auto'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.user)
    async def automine(self, ctx):
        """Switches the automining status."""

        # Check if user exists
        if self.bot.database.get_user_bal(ctx.author.id) is None:
            await ctx.reply(embed=self.bot.error_noacc())
            return
        
        if self.bot.database.get_auto_miner(ctx.author.id):
            dead = self.autominer_died_embed(ctx.author.id)
        result = self.bot.database.update_user_automining_status(ctx.author.id)
        embed=discord.Embed(title=f"You have switched to {"Auto-Mining" if result else "Manual Mining"}!", color=EMB_COLOUR) # Replies to user of result
        await ctx.reply(embed=embed)
        try: await ctx.reply(embed=dead)
        except: pass
    
    def autominer_embed(self, curr_block, user_automine_status):
        # Generates autominer info embed
        embed=discord.Embed(title=f"You are automining block #{curr_block[0]}!", color=EMB_COLOUR, timestamp=datetime.now())
        embed.set_thumbnail(url=self.emb_thumbnail_link)
        embed.add_field(name="✅ Session Hashes", value=f"`{user_automine_status[2]}` Hashes")
        embed.add_field(name="⛏️ Session Blocks Broken", value=f"`{user_automine_status[1]}` Blocks")
        embed.add_field(name="💸 Session Payout", value=f"`{user_automine_status[3]}` {self.display_currency}", inline=False)
        embed.add_field(name="⏱️ Session Start Time", value=f"<t:{user_automine_status[4]}:f>", inline=False)

        # Return built embed
        return embed
    
    def autominer_died_embed(self, uuid):
        # Generates autominer info embed when the autominer dies (or is turned off)
        user_automine_status = self.bot.database.get_auto_miner(uuid)
        embed=discord.Embed(title=f"Your autominer has stopped!", description="Your autominer statistics:", color=EMB_COLOUR, timestamp=datetime.now())
        embed.set_thumbnail(url=self.emb_thumbnail_link)
        embed.add_field(name="✅ Total Hashes Submitted", value=f"`{user_automine_status[2]}` Hashes")
        embed.add_field(name="⛏️ Total Blocks Broken", value=f"`{user_automine_status[1]}` Blocks")
        embed.add_field(name="💸 End Session Payout", value=f"`{user_automine_status[3]}` {self.display_currency}", inline=False)
        embed.add_field(name="⏱️ Automining Start Time", value=f"<t:{user_automine_status[4]}:f>", inline=False)

        return embed
    
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
                curr_block = self.bot.database.get_current_block_relevant_md()
                share_sum = self.bot.database.get_pool_share_sum()[0]
                user_pool_shares = self.bot.database.get_pool_miner(ctx.author.id)[2]

                embed=discord.Embed(title=f"Pool Statistics", description=f"These are the current pool\nstatistics for block #{curr_block[0]}.", color=EMB_COLOUR, timestamp=datetime.now())
                embed.set_thumbnail(url=self.emb_thumbnail_link)
                embed.add_field(name="✅ Shares You Submitted", value=f"`{user_pool_shares}` Shares", inline=False)
                embed.add_field(name="🌎 Global Shares Submitted", value=f"`{share_sum}` Shares")
                if user_pool_shares != 0:
                    embed.add_field(name="💵 Estimated Pool Reward", value=f"`{curr_block[1]*(user_pool_shares/share_sum):.6f}` {self.display_currency}", inline=False)
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
            await ctx.reply(embed=self.bot.success_embed(f"You have switched to {result} Mining!")) # Replies to user of result
        else: await ctx.reply(embed=self.bot.error_noacc())

async def setup(bot):
    await bot.add_cog(Mining(bot))