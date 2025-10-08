import discord
from discord import app_commands
from io import BytesIO
from PIL import Image, ImageDraw
import os

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Folder setup
SAVE_FOLDER = r"C:\Users\asus\OneDrive\Desktop\Pfp Clips"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Helper function to clip an avatar into a circle and save it
async def clip_avatar(member: discord.Member):
    avatar = member.display_avatar.replace(size=256, format='png')
    buffer = BytesIO()
    await avatar.save(buffer)
    buffer.seek(0)

    img = Image.open(buffer).convert("RGBA")
    size = img.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)

    save_path = os.path.join(SAVE_FOLDER, f"{member.name}_clipped_pfp.png")
    img.save(save_path, "PNG")

    return save_path

# Single PFP clip command
@tree.command(name="clip_pfp", description="Clip a member's profile picture into a circle and save it.")
@app_commands.describe(member="The member whose profile picture you want to clip")
async def clip_pfp(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    await interaction.response.defer()
    path = await clip_avatar(member)
    await interaction.followup.send(f"✅ Clipped {member.display_name}'s profile picture!")

# All PFPs clip command
@tree.command(name="clip_all", description="Clip all non-bot members' profile pictures and save them.")
async def clip_all(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    clipped = 0

    for member in guild.members:
        if member.bot:
            continue
        try:
            await clip_avatar(member)
            clipped += 1
        except Exception as e:
            print(f"Failed to clip {member.name}: {e}")

    await interaction.followup.send(f" Clipped {clipped} profile pictures!")

# Sync commands when bot is ready
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Slash commands synced.")

# Run bot
bot.run("MTM2NzA5Nzg3MzUyNjk0Nzg0MA.GHmIcK.Z2rFCzYmXno0_d332BzoKZxe3FfSOFiXr385Wg")


