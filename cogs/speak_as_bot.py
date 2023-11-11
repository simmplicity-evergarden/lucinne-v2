from discord.ext import tasks, commands
from discord import app_commands
#from discord import app_commands
import discord
#import petrify_logic
#import json
#import helpers
#import time
import logging
#from random import randint
#from random import choice
#from typing import Literal
from typing import Optional
from settings import *
from helpers import *

logger = logging.getLogger('bot')

class Speak_as_Bot_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded Speak-as-Bot')

	async def cog_load(self):
		target_guild = self.bot.get_guild(config.getint('guild','guild_id'))
		for webhook in await target_guild.webhooks():
			if webhook.name == 'rosa_bot':
				self.webhook = webhook
				# Track this separately since it seems to get lost
				config['runtime']['webhook_channel'] = str(webhook.channel_id)

	@app_commands.command(description='Speak as a bot')
	async def speak(self, inter: discord.Interaction, *, message: str):
		logger.debug(f'{inter.user.display_name} speaks through the bot: {message}')


		# Move webhook if needed
		if config.getint('runtime','webhook_channel') != inter.channel.id:
			await self.webhook.edit(channel=inter.channel)
			config['runtime']['webhook_channel'] = str(inter.channel.id)

		await self.webhook.send(message, username=inter.user.display_name, avatar_url=inter.user.display_avatar.url, wait=True)

		await inter.response.send_message('confirmed',ephemeral=True,delete_after=0.1)
