import discord
import random
from discord.ext import commands
from datetime import datetime

EMB_COLOUR = 0x000000
COOLDOWN = 2

class User(commands.Cog):
    """
    User commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.default_prefix = bot.config["prefixes"][0]
        self.display_currency = bot.config["display_currency"]

    @commands.command()
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def create(self, ctx):
        """Creates a wallet account."""
        if self.bot.database.create_user(ctx.author.id, ctx.author.name) is not False:
            await ctx.send(f"Congratulations! Your account has been made. Run `{self.default_prefix}help` for more commands to continue!")
            await self.balance(ctx, str(ctx.author.id))
        else:
            await ctx.send(embed=self.bot.error_embed("You already have an account!"))
    
    @commands.command(aliases=['b','bal','bank','wallet'])
    @commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
    async def balance(self, ctx, *member):
        """Shows account balance."""
        member = ''.join(member).strip('<@>')
        defaulted = False

        try: member = await ctx.bot.fetch_user(member)
        except: member = ctx.author; defaulted = True
        finally:
            userData = self.bot.database.get_user(member.id)

            if userData is not None:
                # Check if username updated
                if member.name != userData[4]:
                    self.bot.database.update_username(member.id, member.name)
                    print(f"Updated username in database: {userData[4]} -> {member.name}")

                # Defaults to author's if member mentionned couldn't be found
                if defaulted or member.id == ctx.author.id: embTitle = "Your Balance"
                else: embTitle = f"{member.name}\'s Balance"

                # Embed building
                embed=discord.Embed(title=embTitle, color=EMB_COLOUR, timestamp=datetime.now())
                try: embed.set_thumbnail(url=member.avatar.url)
                except: embed.set_thumbnail(url=f'https://cdn.discordapp.com/embed/avatars/{random.randint(0,5)}.png')    
                embed.add_field(name="💵 Currency", value=f"{userData[1]} {self.display_currency}", inline=False)
                embed.add_field(name="☑️ Blocks", value=f"{userData[2]:,} block{'s' if userData[2] != 1 else ""} broken", inline=False)
                embed.add_field(name="🚤 Pooling", value=f"{"TRUE" if userData[3] == 1 else "FALSE"}", inline=False)
                embed.set_footer(text="Bot made with ❤️ by eld_!")
                await ctx.reply(embed=embed)
            else:
                if defaulted or member.id == ctx.author.id: 
                    await self.create(ctx)
                else:
                    await ctx.reply(embed=self.bot.error_embed(f"{member.name} does not have an account!"))

async def setup(bot):
    await bot.add_cog(User(bot))