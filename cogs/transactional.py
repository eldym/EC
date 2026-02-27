import discord
import asyncio
from discord.ext import commands
from datetime import datetime

COOLDOWN = 2
EMB_COLOUR = 0x000000

class Transactional(commands.Cog):
    """
    Transaction commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.display_currency = bot.config["display_currency"]
        self.emb_thumbnail_link = bot.config["emb_thumbnail_link"]

    @commands.command(aliases=['p', 'pay', 'give'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def send(self, ctx, reciever, amount):
        """Send a reciever an amount of currency."""
        # CHECKS
        sender_data = float(self.bot.database.get_user_bal(ctx.author.id)[0])
        # check if user has account
        if sender_data is None: 
            await ctx.reply(embed=self.bot.noacc())
            return
        
        # check if reciever string is valid
        reciever_id = ''.join(reciever).strip('<@>')
        if not reciever_id.isdigit():
            await ctx.reply(embed=self.bot.error_embed("Reciever field is invalid!"))
            return
        
        # check if reciever is sender
        if reciever_id == str(ctx.author.id):
            await ctx.reply(embed=self.bot.error_embed("You can't send yourself currency!"))
            return
        
        # check if reciever has account
        reciever_data = self.bot.database.get_user(reciever)
        if reciever_data is None:
            await ctx.reply(embed=self.bot.error_embed("This user doesn't have an account!"))
            return
        
        amount = float(amount)
        # handle 0 / negative item amount
        if amount <= 0:
            await ctx.reply(embed=self.bot.error_embed(f"The amount you want to send must be **greater than or equal** to `0.000001` {self.display_currency}!"))
            return
        
        # user doesn't have enough money
        if sender_data < amount:
            await ctx.reply(embed=self.bot.error_embed(f"You don't have enough {self.display_currency} to make this transaction!"))
            return

        # timed transaction confirmation
        await ctx.reply("Please say \'yes\' or \'y\' within 30 seconds to complete this transaction.")

        # checking function
        def check(m):
            return (m.content.lower() == 'yes' or m.content.lower() == 'y') and m.channel == ctx.channel
        
        # try/except block to check if confirmation was given
        try: msg = await self.bot.wait_for('message', check=check, timeout=30.0) # set to 30 seconds
        except asyncio.TimeoutError: await ctx.reply("The transaction has timed out and was canceled.") # if timer runs out
        else: # If confirmation is made
            reciept = self.bot.database.transaction(ctx.author.id, reciever, amount)
            if type(reciept) is tuple:
                # Embed building
                embed=discord.Embed(title="Transaction Success!", description=f"**{amount:.6f} {self.display_currency}** was sent to **{reciever_data[4]}**.", color=EMB_COLOUR, timestamp=datetime.now())
                embed.add_field(name="🧾 Transaction ID", value=f"`{reciept[0]}`", inline=False)
                embed.add_field(name="🛃 Fee", value=f"`{reciept[4]}` {self.display_currency}", inline=False)
                embed.add_field(name="⏰ Recorded Timestamp", value=f"`{reciept[5]}`", inline=False)
                embed.set_footer(text=f"Currency sent by {ctx.author.name}!")
                await ctx.reply(embed=embed)

                # Notify reciever
                reciever_user = await ctx.bot.fetch_user(reciever)
                await reciever_user.send(f"Hey <@{reciever}>! You recieved {amount:.6f} {self.display_currency} from **{ctx.author.name}**!\nTransaction ID: `{reciept[0]}`\n-# You can view this transaction using `!transaction {reciept[0]}`")
            else:
                # If there is an error, prints out error to user
                await ctx.reply(f"`Error!`\n{reciept}")

    @commands.command(aliases=['t', 'tran', 'log', 'reciept'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def transaction(self, ctx, id):
        """Displays transaction information given an txn ID."""
        transaction = self.bot.database.get_transaction(id)

        # Checks if transaction exists
        if transaction is not None:
            # Embed building
            embed=discord.Embed(title=f"Transaction #{transaction[0]} Information", color=EMB_COLOUR)
            embed.set_thumbnail(url=self.emb_thumbnail_link)

            # Get user datum
            sender_id = transaction[1]
            if sender_id != "Coinbase": sender_name = self.bot.database.get_username(sender_id)[0]
            else: 
                sender_name = "Coinbase"
                sender_id = "NEWLY_MINTED"

            reciever_id = transaction[2]
            reciever_name = self.bot.database.get_username(reciever_id)[0]

            embed.add_field(name="📤 Sender", value=f"{sender_name} (`{sender_id}`)", inline=False)
            embed.add_field(name="📥 Reciever", value=f"{reciever_name} (`{reciever_id}`)", inline=False)
            embed.add_field(name="💵 Amount", value=f"`{transaction[3]}` {self.display_currency}", inline=False)
            embed.add_field(name="🛃 Fee", value=f"`{transaction[4]}` {self.display_currency}", inline=False)
            embed.add_field(name="⏱️ Time", value=f"<t:{transaction[5]}:f>", inline=False)
            embed.set_footer(text=f"Currency sent by {sender_name}!")
            await ctx.reply(embed=embed)
        
        # If transaction doesn't exist, throw error embed
        else: await ctx.reply(embed=self.bot.error_nodata())

    """@commands.command(aliases=['ts','trans'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def transactions(self, ctx, *inputs):
        if inputs is not None and len(inputs.split()) < 3:
            inputs.split()"""
        
async def setup(bot):
    await bot.add_cog(Transactional(bot))