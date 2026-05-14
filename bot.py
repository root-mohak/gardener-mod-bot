import discord

from discord.ext import commands
from datetime import timedelta

# ======================================================
# MODERATION COG
# ======================================================

class Moderation(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # ==================================================
    # KICK COMMAND
    # ==================================================

    @commands.command()

    @commands.has_permissions(
        kick_members=True
    )

    async def kick(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason provided"
    ):

        try:

            await member.kick(
                reason=reason
            )

            embed = discord.Embed(
                title="👢 Member Kicked",
                description=(
                    f"{member.mention} "
                    f"was kicked."
                ),
                color=discord.Color.red()
            )

            embed.add_field(
                name="Reason",
                value=reason,
                inline=False
            )

            await ctx.send(embed=embed)

        except Exception as e:

            await ctx.send(
                f"❌ Error: `{e}`"
            )

    # ==================================================
    # BAN COMMAND
    # ==================================================

    @commands.command()

    @commands.has_permissions(
        ban_members=True
    )

    async def ban(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason provided"
    ):

        try:

            await member.ban(
                reason=reason
            )

            embed = discord.Embed(
                title="🔨 Member Banned",
                description=(
                    f"{member.mention} "
                    f"was banned."
                ),
                color=discord.Color.dark_red()
            )

            embed.add_field(
                name="Reason",
                value=reason,
                inline=False
            )

            await ctx.send(embed=embed)

        except Exception as e:

            await ctx.send(
                f"❌ Error: `{e}`"
            )

    # ==================================================
    # UNBAN COMMAND
    # ==================================================

    @commands.command()

    @commands.has_permissions(
        ban_members=True
    )

    async def unban(
        self,
        ctx,
        user_id: int
    ):

        try:

            user = await self.bot.fetch_user(
                user_id
            )

            await ctx.guild.unban(user)

            await ctx.send(
                f"✅ Unbanned `{user}`"
            )

        except Exception as e:

            await ctx.send(
                f"❌ Error: `{e}`"
            )

    # ==================================================
    # TIMEOUT COMMAND
    # ==================================================

    @commands.command()

    @commands.has_permissions(
        moderate_members=True
    )

    async def timeout(
        self,
        ctx,
        member: discord.Member,
        minutes: int,
        *,
        reason="No reason provided"
    ):

        try:

            await member.timeout(
                timedelta(minutes=minutes),
                reason=reason
            )

            embed = discord.Embed(
                title="⏳ Member Timed Out",
                description=(
                    f"{member.mention} "
                    f"timed out for "
                    f"{minutes} minutes."
                ),
                color=discord.Color.orange()
            )

            embed.add_field(
                name="Reason",
                value=reason,
                inline=False
            )

            await ctx.send(embed=embed)

        except Exception as e:

            await ctx.send(
                f"❌ Error: `{e}`"
            )

    # ==================================================
    # CLEAR COMMAND
    # ==================================================

    @commands.command()

    @commands.has_permissions(
        manage_messages=True
    )

    async def clear(
        self,
        ctx,
        amount: int
    ):

        try:

            deleted = await ctx.channel.purge(
                limit=amount + 1
            )

            msg = await ctx.send(
                f"🧹 Deleted "
                f"`{len(deleted)-1}` messages."
            )

            await msg.delete(delay=3)

        except Exception as e:

            await ctx.send(
                f"❌ Error: `{e}`"
            )

    # ==================================================
    # LOCKDOWN COMMAND
    # ==================================================

    @commands.command()

    @commands.has_permissions(
        manage_channels=True
    )

    async def lockdown(self, ctx):

        try:

            overwrite = (
                ctx.channel.overwrites_for(
                    ctx.guild.default_role
                )
            )

            overwrite.send_messages = False

            await ctx.channel.set_permissions(
                ctx.guild.default_role,
                overwrite=overwrite
            )

            await ctx.send(
                "🔒 Channel locked."
            )

        except Exception as e:

            await ctx.send(
                f"❌ Error: `{e}`"
            )

    # ==================================================
    # UNLOCK COMMAND
    # ==================================================

    @commands.command()

    @commands.has_permissions(
        manage_channels=True
    )

    async def unlock(self, ctx):

        try:

            overwrite = (
                ctx.channel.overwrites_for(
                    ctx.guild.default_role
                )
            )

            overwrite.send_messages = True

            await ctx.channel.set_permissions(
                ctx.guild.default_role,
                overwrite=overwrite
            )

            await ctx.send(
                "🔓 Channel unlocked."
            )

        except Exception as e:

            await ctx.send(
                f"❌ Error: `{e}`"
            )

# ======================================================
# SETUP
# ======================================================

async def setup(bot):

    await bot.add_cog(
        Moderation(bot)
    )
