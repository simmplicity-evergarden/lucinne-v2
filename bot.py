from discord.ext import commands, tasks
import discord
import logging

import guilds

# Cogs import

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = False
intents.invites = False
intents.voice_states = False
intents.typing = False
intents.guild_scheduled_events = False
intents.auto_moderation_configuration = False
intents.auto_moderation_execution = False


bot = commands.Bot(command_prefix='!!', intents=intents)
logger = logging.getLogger('bot')

@bot.event
async def on_ready():
	logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
	logger.info('---------------------------------------------')
	await bot.load_extension("cogs.common")
	await bot.load_extension("cogs.rename_cog")
	await bot.load_extension("cogs.role_manager_cog")
	await bot.load_extension("cogs.configuration_cog")
	await bot.load_extension("cogs.thrall_cog")
	await bot.load_extension("cogs.robot_cog")
	await bot.load_extension("cogs.feral_cog")
	await bot.load_extension("cogs.squeak_cog")
	await bot.load_extension("cogs.object_cog")
	await bot.load_extension("cogs.router")
	await bot.load_extension("cogs.squeak_censor_cog")
	await bot.load_extension("cogs.leashing_cog")
	await bot.load_extension("cogs.rx")
	await bot.load_extension("cogs.speak_as_member_cog")
	await bot.load_extension("cogs.silly")
	await bot.load_extension("cogs.shocks")
	sync.start()

@bot.event
async def on_guild_join(guild: discord.Guild):
	guilds.add_guild(guild)

@bot.event
async def on_guild_remove(guild: discord.Guild):
	guilds.remove_guild(guild)

@tasks.loop(seconds=30)
async def sync():
	guilds.bot_guilds.sync()
