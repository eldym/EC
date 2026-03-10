import discord
from discord.ext import commands

class Socials(commands.Cog):
    """
    ### Socials Commands
    Commands with links to EC socials!

    - **github / gh**: github repo link.
    - **discord / dc**: discord server link.
    """
    @commands.command(aliases=['gh'])
    async def github(self, ctx):
        """EC GitHub repo! Check it out :)"""
        embed=discord.Embed(title="GitHub Repo", description="Check out updates on EC's Github repository page:\nhttps://github.com/eldym/EC", color=0x000000)
        embed.set_footer(text="Consider giving a follow or ⭐!")
        embed.set_thumbnail(url=f"https://cdn.discordapp.com/attachments/1328761316847910912/1476724922729631745/25231.png")
        await ctx.reply(embed=embed)
    
    @commands.command(aliases=['dc'])
    async def discord(self, ctx):
        """EC Discord Server! Check it out :)"""
        embed=discord.Embed(title="Discord Server", description="Check out announcements and giveaways at:\nhttps://discord.gg/xqudUnVMAW", color=0x5865f2)
        embed.set_footer(text="Consider joining on the fun!")
        embed.set_thumbnail(url=f"https://cdn.discordapp.com/attachments/791182073263685672/1480804377479479388/Discord-Symbol-Blurple.png")
        await ctx.reply(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Socials(bot))