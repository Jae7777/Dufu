import discord
import os
from dotenv import load_dotenv
import commands as c
import buttons as b

load_dotenv()

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.slash_command(name="help", description="Options")
async def help_command(ctx):
    view=b.Buttons(ctx)
    await ctx.send("Here are the options.",view=view)

@bot.slash_command(name="record", description="Join and start recording")
async def record(ctx: discord.ApplicationContext):
    await c.start_recording(ctx)
    
@bot.slash_command(name="stop", description="Stop recording")
async def stop(ctx: discord.ApplicationContext):
    """Slash command that calls the stop_recording logic."""
    stopped = await c.stop_recording(ctx)
    if stopped:
        await ctx.respond("🛑 Stopping recording...")
    else:
        await ctx.respond("❌ Not recording or not in a voice channel.", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))