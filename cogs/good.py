from discord.ext import commands
import logging
import guilds
import discord
from typing import Optional

logger = logging.getLogger('bot.good')

# Simm
async def is_simm(ctx):
	return (ctx.author.id == 1053028780383424563)


class Good_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded Good')

	@commands.command()
	async def good(self, context: commands.Context, noun: str, goodx: Optional[discord.Member]):
		await self.good_logic(context, goodx, noun)

	async def good_logic(self, 
		context: commands.Context, 
		goodx: Optional[discord.Member], 
		good_type: str = "noun"):
		if goodx is None or context.author.id == goodx.id:
			goodscore = self.get_good(context.guild.id, context.author.id)
			await context.channel.send(f"{context.author.mention} You have a good {good_type} score of {goodscore}.")
		else:
			goodscore = self.add_good(context.guild.id, goodx.id)
			await context.channel.send(f"Good {good_type}! {goodx.display_name} has a good {good_type} score of {goodscore}.")



	# Add one good X point to the list	
	def add_good(self, guild: int, user: int) -> int:
		# Get guild
		if "good" not in guilds.bot_guilds[f"{guild}"].keys():
			guilds.bot_guilds[f"{guild}"]["good"] = {}

		if str(user) not in guilds.bot_guilds[f"{guild}"]["good"].keys():
			guilds.bot_guilds[f"{guild}"]["good"][str(user)] = 1
		else:
			guilds.bot_guilds[f"{guild}"]["good"][str(user)] += 1
		
		return guilds.bot_guilds[f"{guild}"]["good"][str(user)] 

	# Add one good X point to the list
	def get_good(self, guild: int, user: int, good_type: str):
		if "good" not in guilds.bot_guilds[f"{guild}"].keys():
			return 0

		if str(user) not in guilds.bot_guilds[f"{guild}"]["good"].keys():
			return 0

		return guilds.bot_guilds[f"{guild}"]["good"][str(user)] 



async def setup(bot):
	await bot.add_cog(Good_Cog(bot))

