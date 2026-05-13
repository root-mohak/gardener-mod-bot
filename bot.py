import discord
from discord.ext import commands
from datetime import timedelta

# =========================================
# MODERATION COG
# =========================================

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # KICK COMMAND
    # =====================================

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason"):

        try:

            await member.kick(reason=reason)

            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"{member.mention} was kicked",
                color=discord.Color.red()
            )

            embed.add_field(
                name="Reason",
                value=reason
            )

            await ctx.send(embed=embed)

        except Exception as e:

            await ctx.send(
                f"❌ Error: {e}"
            )

    # =====================================
    # BAN COMMAND
    # =====================================

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason"):

        try:

            await member.ban(reason=reason)

            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"{member.mention} was banned",
                color=discord.Color.dark_red()
            )

            embed.add_field(
                name="Reason",
                value=reason
            )

            await ctx.send(embed=embed)

        except Exception as e:

            await ctx.send(
                f"❌ Error: {e}"
            )

    # =====================================
    # UNBAN COMMAND
    # =====================================

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):

        try:

            user = await self.bot.fetch_user(user_id)

            await ctx.guild.unban(user)

            await ctx.send(
                f"✅ Unbanned {user}"
            )

        except Exception as e:

            await ctx.send(
                f"❌ Error: {e}"
            )

    # =====================================
    # TIMEOUT COMMAND
    # =====================================

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx,
        member: discord.Member,
        minutes: int
    ):

        try:

            duration = timedelta(minutes=minutes)

            await member.timeout(duration)

            await ctx.send(
                f"⏳ {member.mention} timed out for {minutes} minutes"
            )

        except Exception as e:

            await ctx.send(
                f"❌ Error: {e}"
            )

    # =====================================
    # CLEAR COMMAND
    # =====================================

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):

        try:

            await ctx.channel.purge(limit=amount + 1)

            msg = await ctx.send(
                f"🧹 Deleted {amount} messages"
            )

            await msg.delete(delay=3)

        except Exception as e:

            await ctx.send(
                f"❌ Error: {e}"
            )

    # =====================================
    # LOCKDOWN COMMAND
    # =====================================

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx):

        overwrite = ctx.channel.overwrites_for(
            ctx.guild.default_role
        )

        overwrite.send_messages = False

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite
        )

        await ctx.send(
            "🔒 Channel locked"
        )

    # =====================================
    # UNLOCK COMMAND
    # =====================================

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):

        overwrite = ctx.channel.overwrites_for(
            ctx.guild.default_role
        )

        overwrite.send_messages = True

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite
        )

        await ctx.send(
            "🔓 Channel unlocked"
        )

# =========================================
# SETUP
# =========================================

async def setup(bot):
    await bot.add_cog(Moderation(bot))
