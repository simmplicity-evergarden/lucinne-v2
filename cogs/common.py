from discord.ext import commands
import discord
import logging

logger = logging.getLogger('bot')

class Common_Cog(commands.Cog):

	def __init__(self, bot):
		logger.info('Loaded Common')

	# Sync commands
	@commands.command(description='Sync bot commands w/ server')
	async def sync(self, context: commands.Context):
		logger.info(f"Ran a manual command sync with {context.guild.id} ({context.guild.name})")
		synced = await context.bot.tree.sync()
		await context.send(f'Sync\'d {len(synced)} commands to current guild.', ephemeral=True)
