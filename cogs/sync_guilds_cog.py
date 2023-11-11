from discord.ext import tasks, commands
import guilds
import logging

logger = logging.getLogger("bot.sync")

class Sync_Guilds_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.synchronize_guilds_shelf.start()

	def cog_unload(self):
		self.synchronize_guilds_shelf.cancel()

	@tasks.loop(seconds=30.0)
	async def synchronize_guilds_shelf(self):
		# Doing this because I think it's necessary for it to save properly
		for key,value in guilds.bot_guilds.items:
			guilds.bot_guilds[key] = value

		guilds.bot_guilds.sync()
		logger.debug("Ran shelve sync")
