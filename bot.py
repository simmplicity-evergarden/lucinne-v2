from discord.ext import commands, tasks
import discord
import logging

import guilds

# Cogs import
import cogs.common
import cogs.rename_cog
import cogs.role_manager_cog
import cogs.thrall_cog
import cogs.robot_cog
import cogs.feral_cog
import cogs.squeak_cog
import cogs.leashing_cog
import cogs.router
import cogs.configuration_cog

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
	await bot.add_cog(cogs.common.Common_Cog(bot))
	await bot.add_cog(cogs.rename_cog.Rename_Cog(bot))
	await bot.add_cog(cogs.role_manager_cog.Role_Manager_Cog(bot))
	await bot.add_cog(cogs.configuration_cog.Configuration_Cog(bot))
	await bot.add_cog(cogs.thrall_cog.Thrall_Cog(bot))
	await bot.add_cog(cogs.robot_cog.Robot_Cog(bot))
	await bot.add_cog(cogs.feral_cog.Feral_Cog(bot))
	await bot.add_cog(cogs.squeak_cog.Squeak_Cog(bot))
	await bot.add_cog(cogs.leashing_cog.Leashing_Cog(bot))
	await bot.add_cog(cogs.router.SpeechRouter_Cog(bot))
	sync.start()

@bot.event
async def on_guild_join(guild: discord.Guild):
	guilds.add_guild(guild)

@bot.event
async def on_guild_remove(guild: discord.Guild):
	guilds.remove_guild(guild)

@tasks.loop(seconds=10)
async def sync():
	guilds.bot_guilds.sync()
