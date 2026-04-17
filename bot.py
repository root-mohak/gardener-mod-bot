import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import timedelta
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# VERIFY SYSTEM
# =========================
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)
        button = Button(label="I Agree ✅", style=discord.ButtonStyle.success)
        button.callback = self.verify_user
        self.add_item(button)

    async def verify_user(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        member = discord.utils.get(guild.roles, name="💻 Member")
        new = discord.utils.get(guild.roles, name="🌿 New Joiner")

        if new:
            await user.remove_roles(new)
        if member:
            await user.add_roles(member)

        await interaction.response.send_message(
            "✅ Verified! Full access unlocked 🚀",
            ephemeral=True
        )

# =========================
# INTEREST SYSTEM
# =========================
ROLE_MAP = {
    "Psychology": "🧠 Psychology",
    "Markets": "📈 Markets",
    "Startups": "🚀 Startups",
    "Programming": "💻 Programming",
    "AI ML": "🤖 AI / ML",
    "Cybersecurity": "🛡️ Cybersecurity"
}

class InterestView(View):
    def __init__(self):
        super().__init__(timeout=None)

        for key, label in ROLE_MAP.items():
            button = Button(label=label, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(key)
            self.add_item(button)

    def create_callback(self, key):
        async def callback(interaction: discord.Interaction):
            role_name = ROLE_MAP[key]
            role = discord.utils.get(interaction.guild.roles, name=role_name)

            if not role:
                await interaction.response.send_message(
                    f"{role_name} not found ❌",
                    ephemeral=True
                )
                return

            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"Removed {role_name}",
                    ephemeral=True
                )
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"Added {role_name}",
                    ephemeral=True
                )

        return callback

# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    bot.add_view(InterestView())
    print(f"{bot.user} is online 🌱")


@bot.event
async def on_member_join(member):
    guild = member.guild

    new = discord.utils.get(guild.roles, name="🌿 New Joiner")
    if new:
        await member.add_roles(new)

    welcome = discord.utils.get(guild.text_channels, name="welcome")
    interest = discord.utils.get(guild.text_channels, name="choose-your-interests")

    if welcome:
        await welcome.send(
            f"""
🌱 Welcome {member.mention}

### Builder’s Collective

1️⃣ Click **I Agree**  
2️⃣ Choose interests  
3️⃣ Introduce yourself  

🚀 Unlock full access after verification
""",
            view=VerifyView()
        )

    if interest:
        await interest.send(
            f"{member.mention} choose your interests 👇",
            view=InterestView()
        )

# =========================
# FILTER
# =========================
BAD_WORDS = {"fk","idiot","stupid","dumb","madarchod","bhosdike"}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if any(w in message.content.lower() for w in BAD_WORDS):
        await message.delete()
        await message.channel.send(
            f"{message.author.mention} maintain etiquette ⚠️"
        )

    await bot.process_commands(message)

# =========================
# ERROR HANDLING
# =========================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("User not found ❌")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments ❌")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("No permission ❌")
    else:
        print(error)

# =========================
# COMMANDS
# =========================
@bot.command()
async def ping(ctx):
    await ctx.send("GardenerMod active 🌱")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    await member.timeout(timedelta(minutes=minutes))
    await ctx.send(f"{member.mention} timed out")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await member.add_roles(role)
        await ctx.send("Role added ✅")
    else:
        await ctx.send("Role not found ❌")

# 🚀 BUILDER COMMAND
@bot.command()
@commands.has_permissions(manage_roles=True)
async def builder(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="🚀 Active Builder")

    if role:
        await member.add_roles(role)
        await ctx.send(f"{member.mention} is now a Builder 🚀")
    else:
        await ctx.send("Builder role not found ❌")

# =========================
# CHANNEL CONTROL
# =========================
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lockchannel(ctx):
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"🔒 {ctx.channel.mention} locked")
    except:
        await ctx.send("Error ❌")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlockchannel(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send(f"🔓 {ctx.channel.mention} unlocked")

# =========================
# INTEREST COMMAND
# =========================
@bot.command()
async def interests(ctx):
    await ctx.send("Select interests 👇", view=InterestView())

# =========================
# STARTER MESSAGES
# =========================
@bot.command()
@commands.has_permissions(administrator=True)
async def setupmessages(ctx):
    guild = ctx.guild

    general = discord.utils.get(guild.text_channels, name="general")
    intro = discord.utils.get(guild.text_channels, name="introductions")

    if general:
        await general.send("""
🚀 Welcome to the Builder Network

Drop:
• What you're learning
• What you want to build
""")

    if intro:
        await intro.send("""
👋 Introduce Yourself:

• What are you learning?
• What do you want to build?
• Your main interest?
""")

    await ctx.send("✅ Starter messages sent")

# =========================
# BUILD TRIGGER
# =========================
@bot.command()
async def startbuild(ctx):
    await ctx.send("""
🚀 Build in Public

• What are you building?
• What problem are you solving?
• Next step?
""")

# =========================
bot.run(TOKEN)
