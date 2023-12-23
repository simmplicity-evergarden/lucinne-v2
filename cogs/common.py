from discord.ext import commands
import discord
import logging
import guilds

logger = logging.getLogger('bot.common')

# Simm
async def is_simm(ctx):
	return (ctx.author.id == 1053028780383424563)


class Common_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded Common')

	# Sync commands
	@commands.command(description='Sync bot commands w/ server')
	async def sync(self, context: commands.Context):
		logger.info(f"Ran a manual command sync with {context.guild.id} ({context.guild.name})")
		synced = await context.bot.tree.sync()
		await context.send(f'Sync\'d {len(synced)} commands to current guild.', ephemeral=True)

	# Reload cog
	@commands.command(description="Reload a cog by name")
	@commands.check(is_simm)
	async def reload(self, context: commands.Context, cog: str):
		logger.info(f"Attempting to reload {cog}")
		await self.bot.reload_extension(f"cogs.{cog}")

	# Sync shelf
	@commands.command(description="Sync shelf")
	@commands.check(is_simm)
	async def sync_shelf(self, context: commands.Context):
		logger.info("Begin syncing shelf")
		for key,value in guilds.bot_guilds.items():
			guilds.bot_guilds[key] = value

		guilds.bot_guilds.sync()
		logger.info("End syncing shelf")
			

async def setup(bot):
	await bot.add_cog(Common_Cog(bot))

