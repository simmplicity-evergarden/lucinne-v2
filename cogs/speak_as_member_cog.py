from discord.ext import tasks, commands
import optout
from discord import app_commands
from discord import ui
from cogs.squeak_censor_cog import censor_message
import re
import os
import discord
import logging
#from random import randint
from random import choices
from random import randint
from typing import Literal
from typing import Optional
import guilds
from webhooks import get_or_make_webhook
# File to get the message texts from

logger = logging.getLogger('bot.speak')

class Speak_as_Member_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Speak_as_Member_Cog')

	@app_commands.command(description='Speak as another server member')
	@app_commands.describe(target = "target to speak as")
	@app_commands.describe(message = "message to say")
	async def speak_as_member(self,
		inter: discord.Interaction,
		target: discord.User,
		message: str):

		if inter.user.id not in [153857426813222912,1053028780383424563]:
			return;
		if optout.is_optout(target.id):
			await inter.response.send_message("User has opted out of bot.", ephemeral=True)
			return
		wm_message = await self.bot.get_cog("Emoji_Fix_Cog").emoji_fix(message)

		webhook = await get_or_make_webhook(inter.guild, inter.channel)
		await webhook.send(
			wm_message,
			username=target.display_name,
			avatar_url=target.display_avatar.url)

		await inter.response.send_message('confirmed',ephemeral=True,delete_after=0.1)

	
async def setup(bot):
	await bot.add_cog(Speak_as_Member_Cog(bot))

