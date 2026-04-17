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
            "✅ Verified! You now have access.",
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
Welcome {member.mention} 🌱

1️⃣ Read rules  
2️⃣ Click verify  
3️⃣ Choose interests  

Then introduce yourself 🚀
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

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lockchannel(ctx):
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔒 Locked")
    except:
        await ctx.send("Error ❌")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlockchannel(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Unlocked")

@bot.command()
async def interests(ctx):
    await ctx.send("Select interests 👇", view=InterestView())
@bot.command()
@commands.has_permissions(administrator=True)
async def setupserver(ctx):
    guild = ctx.guild

    # =========================
    # CREATE ROLES
    # =========================
    roles = {
        "🌿 New Joiner": discord.Permissions(view_channel=True),
        "💻 Member": discord.Permissions(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        ),
        "🚀 Active Builder": discord.Permissions(
            view_channel=True,
            send_messages=True
        ),
        "💎 Premium": discord.Permissions(
            view_channel=True,
            send_messages=True
        )
    }

    created_roles = {}

    for name, perms in roles.items():
        role = discord.utils.get(guild.roles, name=name)
        if not role:
            role = await guild.create_role(name=name, permissions=perms)
        created_roles[name] = role

    # =========================
    # CREATE CATEGORY: ONBOARDING
    # =========================
    onboarding = await guild.create_category("👋 Onboarding")

    # Permission setup
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        created_roles["🌿 New Joiner"]: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True
        ),
        created_roles["💻 Member"]: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True
        )
    }

    # =========================
    # CREATE CHANNELS
    # =========================
    await guild.create_text_channel("welcome", category=onboarding, overwrites=overwrites)
    await guild.create_text_channel("rules-and-etiquette", category=onboarding, overwrites=overwrites)
    await guild.create_text_channel("introductions", category=onboarding, overwrites=overwrites)
    await guild.create_text_channel("choose-your-interests", category=onboarding, overwrites=overwrites)

    # =========================
    # GENERAL CATEGORY
    # =========================
    general_cat = await guild.create_category("💬 Community")

    general_overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        created_roles["💻 Member"]: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True
        )
    }

    await guild.create_text_channel("general", category=general_cat, overwrites=general_overwrites)
    await guild.create_text_channel("daily-checkin", category=general_cat, overwrites=general_overwrites)

    await ctx.send("✅ Server fully setup with permissions!")    
@bot.command()
@commands.has_permissions(administrator=True)
async def fullsetup(ctx):
    guild = ctx.guild

    await ctx.send("⚙️ Setting up full server...")

    # =========================
    # CREATE ROLES
    # =========================
    roles = [
        "🌿 New Joiner",
        "💻 Member",
        "🚀 Active Builder",
        "💎 Premium"
    ]

    role_objs = {}

    for role_name in roles:
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name)
        role_objs[role_name] = role

    # =========================
    # CLEAR OLD CHANNELS (OPTIONAL)
    # =========================
    for channel in guild.channels:
        try:
            await channel.delete()
        except:
            pass

    # =========================
    # ONBOARDING CATEGORY
    # =========================
    onboarding_overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        role_objs["🌿 New Joiner"]: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )
    }

    onboarding = await guild.create_category("👋 Onboarding", overwrites=onboarding_overwrites)

    await guild.create_text_channel("welcome", category=onboarding)
    await guild.create_text_channel("rules-and-etiquette", category=onboarding)
    await guild.create_text_channel("introductions", category=onboarding)
    await guild.create_text_channel("choose-your-interests", category=onboarding)

    # =========================
    # COMMUNITY CATEGORY
    # =========================
    community_overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        role_objs["💻 Member"]: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )
    }

    community = await guild.create_category("💬 Community", overwrites=community_overwrites)

    await guild.create_text_channel("general", category=community)
    await guild.create_text_channel("daily-checkin", category=community)
    await guild.create_text_channel("off-topic", category=community)

    # =========================
    # DISCUSSIONS CATEGORY
    # =========================
    discussion = await guild.create_category("🧠 Discussions", overwrites=community_overwrites)

    await guild.create_text_channel("tech", category=discussion)
    await guild.create_text_channel("startups", category=discussion)
    await guild.create_text_channel("markets", category=discussion)
    await guild.create_text_channel("psychology", category=discussion)

    # =========================
    # BUILDERS CATEGORY
    # =========================
    builder_overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        role_objs["🚀 Active Builder"]: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True
        )
    }

    builders = await guild.create_category("🚀 Builders", overwrites=builder_overwrites)

    await guild.create_text_channel("build-in-public", category=builders)
    await guild.create_text_channel("projects-showcase", category=builders)
    await guild.create_text_channel("collaboration-zone", category=builders)

    # =========================
    # PREMIUM CATEGORY
    # =========================
    premium_overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        role_objs["💎 Premium"]: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True
        )
    }

    premium = await guild.create_category("💎 Premium", overwrites=premium_overwrites)

    await guild.create_text_channel("premium-chat", category=premium)
    await guild.create_text_channel("premium-resources", category=premium)

    await ctx.send("✅ FULL SERVER SETUP COMPLETE!")    

bot.run(TOKEN)
