import discord
import asyncio
import time
from discord.ext import commands
from datetime import datetime

COOLDOWN = 2
EMB_COLOUR = 0x000000

class AirdropButton(discord.ui.View):
    def __init__(self, bot, start_time, airdropper_id, timeout = 180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.start_time = start_time
        self.airdropper_id = airdropper_id

    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.airdropper_id:
            await interaction.response.send_message("You cannot claim your own airdrop!", ephemeral=True)
        elif self.bot.database.get_user_bal(interaction.user.id) is None:
            await interaction.response.send_message(embed=self.bot.error_noacc(), ephemeral=True)
        elif self.bot.database.add_airdrop_participant(self.start_time, interaction.user.id):
            await interaction.response.send_message("You joined the airdrop!", ephemeral=True)
        else:
            await interaction.response.send_message("You've already joined the airdrop!", ephemeral=True)

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
        sender_data = float(self.bot.database.get_user_bal(ctx.author.id))
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
        
        # confirm amount is a valid float with 6 decimal places
        try: 
            amount = round(float(amount), 6)
        except:
            await ctx.reply(embed=self.bot.error_embed("Invalid amount!"))
            return
        
        # handle 0 / negative item amount
        if amount < 0.000001:
            await ctx.reply(embed=self.bot.error_embed(f"The amount you want to send must be **greater than or equal** to `0.000001` {self.display_currency}!"))
            return

        # user doesn't have enough money
        if sender_data < amount:
            await ctx.reply(embed=self.bot.error_embed(f"You don't have enough {self.display_currency} to make this transaction!"))
            return

        # timed transaction confirmation
        to_edit = await ctx.reply("Please say \'yes\' or \'y\' within 15 seconds to complete this transaction.")

        # checking function
        def check(m):
            return (m.content.lower() == 'yes' or m.content.lower() == 'y') and m.channel == ctx.channel
        
        # try/except block to check if confirmation was given
        try: msg = await self.bot.wait_for('message', check=check, timeout=15.0) # set to 30 seconds
        except asyncio.TimeoutError: await to_edit.edit(content="The transaction has timed out and was canceled.") # if timer runs out
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

    @commands.command(aliases=['ad', 'drop'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def airdrop(self, ctx, amt, time_period=60):
        """Creates a "drop" where any users interacting with the message within a time period recieve an amount of currency. This amount is split amongst participants."""
        user_bal = self.bot.database.get_user_bal(ctx.author.id)
        if user_bal is None:
            await ctx.reply(embed=self.bot.error_noacc())
            return
        else:
            user_bal = float(user_bal)

        try: amt = round(float(amt), 6)
        except: 
            if amt == "all":
                amt == user_bal
            else:
                await ctx.reply(embed=self.bot.error_embed("Invalid amount!"))
                return

        if amt <= 0:
            await ctx.reply(embed=self.bot.error_embed(f"The amount you want to send must be **greater than or equal** to `0.000001` {self.display_currency}!"))
            return
        
        if amt > user_bal:
            await ctx.reply(embed=self.bot.error_embed(f"You don't have enough {self.display_currency} to make run this airdrop!"))
        
        try: time_period = int(time_period)
        except: time_period = 60
        if time_period > 86400: # limits time periods to only 1 day max
            time_period = 86400

        # timed confirmation
        to_edit = await ctx.reply("Please say \'yes\' or \'y\' within 15 seconds to confirm.")
        def check(m):
            return (m.content.lower() == 'yes' or m.content.lower() == 'y') and m.channel == ctx.channel
        try: msg = await self.bot.wait_for('message', check=check, timeout=15.0) # set to 30 seconds
        except asyncio.TimeoutError: await to_edit.edit(content="The transaction has timed out and was canceled.") # if timer runs out
        else: # If confirmation is made
            await to_edit.edit(content=f"**Confirmed!**\nGenerating airdrop of {amt} {self.display_currency}...")

            # temp hold user's money
            start_time = int(time.time())
            self.bot.database.airdrop_start(ctx.author.id, amt, start_time)
            embed=discord.Embed(title=f"Airdrop started by {ctx.author.name}!", description=f"**{amt} {self.display_currency}** is up for grabs!\nEnds in <t:{start_time+time_period}:R>", color=EMB_COLOUR, timestamp=datetime.now())
            to_edit_embed = await ctx.send(embed=embed, view=AirdropButton(self.bot, start_time, ctx.author.id))
            await asyncio.sleep(2)
            await to_edit.delete()
            await asyncio.sleep(time_period)
            results, uuids = self.bot.database.airdrop_payout(start_time)
            if results:
                ppl = "" if len(uuids) != 1 else f"<@{uuids[0]}>"
                i = 0
                if len(uuids) != 1:
                    while i < len(uuids):
                        if i+2 < len(uuids): ppl += f"<@{uuids[i]}>, "
                        elif i+1 != len(uuids): ppl += f"<@{uuids[i]}> "
                        else: ppl += f"and <@{uuids[i]}>"
                        i += 1

                embed=discord.Embed(title=f"{ctx.author.name}'s airdrop has ended!", description=f"**{amt} {self.display_currency}** was collected by {ppl}!", color=EMB_COLOUR, timestamp=datetime.now())
            else:
                embed=discord.Embed(title=f"{ctx.author.name}'s airdrop has ended!", description=f"No one participated in the airdrop! (**{amt} {self.display_currency}** was refunded.)", color=EMB_COLOUR, timestamp=datetime.now())
            await to_edit_embed.edit(embed=embed)
        
    """@commands.command(aliases=['ts','trans'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def transactions(self, ctx, *inputs):
        if inputs is not None and len(inputs.split()) < 3:
            inputs.split()"""
        
async def setup(bot):
    await bot.add_cog(Transactional(bot))