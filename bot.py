import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import timedelta
import os

# =========================
# TOKEN (FROM ENV)
# =========================
TOKEN = os.getenv("TOKEN")


# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# VERIFY BUTTON VIEW
# =========================
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

        button = Button(
            label="I Agree ✅",
            style=discord.ButtonStyle.success
        )
        button.callback = self.verify_user
        self.add_item(button)

    async def verify_user(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        member_role = discord.utils.get(guild.roles, name="💻 Member")
        new_joiner = discord.utils.get(guild.roles, name="🌿 New Joiner")

        if new_joiner:
            await user.remove_roles(new_joiner)

        if member_role:
            await user.add_roles(member_role)

        await interaction.response.send_message(
            "Welcome! You now have full access 🌱",
            ephemeral=True
        )

# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    print(f"{bot.user} is online 🌱")


@bot.event
async def on_member_join(member):
    new_role = discord.utils.get(member.guild.roles, name="🌿 New Joiner")

    if new_role:
        await member.add_roles(new_role)

    channel = discord.utils.get(member.guild.text_channels, name="welcome")

    if channel:
        await channel.send(
            f"Welcome {member.mention} 🌱\n\n"
            f"Please read the rules and click below to continue.",
            view=VerifyView()
        )

# =========================
# MODERATION FILTER
# =========================
BAD_WORDS = {
    "fk", "idiot", "stupid", "dumb",
    "madarchod", "bhosdike"
}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    if any(word in content for word in BAD_WORDS):
        await message.delete()
        await message.channel.send(
            f"{message.author.mention} please maintain etiquette ⚠️"
        )

    await bot.process_commands(message)

# =========================
# BASIC COMMANDS
# =========================
@bot.command()
async def ping(ctx):
    await ctx.send("GardenerMod is active 🌱")


@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    await member.timeout(
        timedelta(minutes=minutes),
        reason="Manual moderation"
    )
    await ctx.send(
        f"{member.mention} timed out for {minutes} minutes"
    )

# =========================
# ROLE COMMANDS
# =========================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if not role:
        await ctx.send("Role not found ❌")
        return

    await member.add_roles(role)
    await ctx.send(f"Added {role.name} to {member.mention} ✅")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if not role:
        await ctx.send("Role not found ❌")
        return

    await member.remove_roles(role)
    await ctx.send(f"Removed {role.name} from {member.mention} ✅")

# =========================
# CHANNEL CONTROL
# =========================
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lockchannel(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False

    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("Channel locked 🔒")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlockchannel(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True

    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("Channel unlocked 🔓")

# =========================
# RUN BOT
# =========================
bot.run(TOKEN)