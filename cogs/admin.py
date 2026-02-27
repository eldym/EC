import asyncio
from discord.ext import commands

class Admin(commands.Cog):
    """
    ### Admin Commands
    Commands for adminstrators of the bot.

    **add_to_bal / ab** {user_id} {amount}: directly add currency to a user's balance

    **create_user / cu** {user_id}: force create an account for a user

    **update_usernames / uu**: update cached username table

    **kill**: kills the bot instance
    """

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['ab'])
    async def add_to_bal(self, ctx, uuid, amount):
        """ADMIN ONLY: Adds balance to a specific user."""
        if ctx.author.id == self.bot.config["admin_id"]:
            uuid = ''.join(uuid).strip('<@>')
            self.bot.database.update_user_bal(uuid, float(self.bot.database.get_user(uuid)[1]) + float(amount))
            print("Updated user", uuid, "by", amount)
            await ctx.reply(f'Updated user funds by: {amount} {self.bot.config["display_currency"]}')

    @commands.command(aliases=['cu'])
    async def create_user(self, ctx, uuid):
        """ADMIN ONLY: Force creates a user to have a balance."""
        if ctx.author.id == self.bot.config["admin_id"]:
            uuid = ''.join(uuid).strip('<@>')
            try: member = await ctx.bot.fetch_user(uuid)
            except Exception as e:
                print("User was not found", e)
                await ctx.reply(f'User was not found. Check terminal for exception.')
            else:
                self.bot.database.create_user(uuid, member.name)
                print("Created user", member.name, uuid)
                await ctx.reply(f'Forced user balance creation.')

    @commands.command(aliases=['uu'])
    async def update_usernames(self, ctx):
        """ADMIN ONLY: Force creates a refresh on username cache."""
        if ctx.author.id == self.bot.config["admin_id"]:
            list_of_users = self.bot.database.get_all_users()
            for user in list_of_users:
                fetched_user = await ctx.bot.fetch_user(user[0])

                if user[4] != fetched_user.name:
                    self.bot.database.update_username(user[0], fetched_user.name)
                    print(f"Updated username in database: {user[4]} -> {fetched_user.name}")
                else: print("Username", user[4], "was unchanged")

            await ctx.reply(f'Updated all usernames where applicable.')

    # DANGER ZONE

    @commands.command()
    async def kill(self, ctx):
        """ADMIN ONLY: Forces the bot to shut down.""" 
        if ctx.author.id == self.bot.config["admin_id"]:
            await ctx.reply("**FORCE SHUTDOWN?**\nPlease say \'yes\' or \'y\' within 15 seconds to complete this action.")
            def check(m):
                return (m.content.lower() == 'yes' or m.content.lower() == 'y') and m.channel == ctx.channel
            # Confirmation for the kill switch
            try: msg = await self.bot.wait_for('message', check=check, timeout=15.0)
            except asyncio.TimeoutError: await ctx.reply("The action has been canceled.") # If timer runs out
            else: 
                exit()
            
async def setup(bot):
    await bot.add_cog(Admin(bot))