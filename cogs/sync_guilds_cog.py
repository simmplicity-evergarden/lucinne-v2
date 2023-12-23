from discord.ext import tasks, commands
import guilds
import logging

logger = logging.getLogger("bot.sync")

class Sync_Guilds_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.synchronize_guilds_shelf.start()
		logger.info("Guild shelf sync started")

	def cog_unload(self):
		self.synchronize_guilds_shelf.cancel()

	@tasks.loop(seconds=30.0)
	async def synchronize_guilds_shelf(self):
		logger.info("Begin shelf sync")
		guilds.bot_guilds.sync()
		logger.info("Finished shelf sync")

async def setup(bot):
	await bot.add_cog(Sync_Guilds_Cog(bot))

