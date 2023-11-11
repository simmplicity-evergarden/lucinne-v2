from discord.ext import tasks, commands
from discord import app_commands
#import re
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
responses_file_location = os.path.join(os.path.dirname(__file__),"..","resources","robot_messages.txt")


logger = logging.getLogger('bot.robot')

class Robot_Cog(commands.Cog):
	class Robot_Affliction():
		# In strict mode, only pre-defined responses are allowed
		strict_mode: bool = False

		def __init__(self, strict_mode: bool=False):
			self.strict_mode = strict_mode

	responses = {}

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Robot_Cog')
		if os.path.exists(responses_file_location):
			with open(responses_file_location, 'r') as responses_file:
				for line in responses_file.readlines():
					# Add responses to dict
					response_item = line.split(',',1)
					if len(response_item) < 2:
						continue
					self.responses[response_item[0]] = response_item[1].strip()
		logger.debug(f"Loaded {len(self.responses)} robot responses from file")

	@app_commands.command(description='Afflict robot on target')
	@app_commands.describe(target = "affliction to assign a role to")
	@app_commands.describe(strict_mode = "only allow pre-set phrases")
	@app_commands.describe(clear = "use this to clear the assigned role; overrides other options")
	async def afflict_robot(self,
						inter: discord.Interaction,
						target: discord.User,
						strict_mode: Optional[bool] = False,
						clear: Optional[Literal["clear"]] = None):

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		affliction = self.Robot_Affliction(strict_mode)

		logger.debug(f"Affliction request: user={target.display_name} strict={strict_mode}")

		if clear is None:
			# Afflict user
			await bot_guild.afflict_target(self.bot, target, affliction)
			await inter.response.send_message(f"Successfully afflicted {target.name}.", ephemeral=True)

		else:
			# Afflict user
			await bot_guild.unafflict_target(self.bot, target, affliction)
			await inter.response.send_message(f"Successfully cleared afflicted {target.name}.", ephemeral=True)


	# Run message relay
	async def on_message(self, message):

		# Get user's affliction settings
		user_list = guilds.bot_guilds[str(message.guild.id)].users
		# To get here, the user must already have the setting,
		# so we can almost guarantee it's in the list
		affliction = next(filter(
			lambda x: type(x).__name__ == self.Robot_Affliction.__name__,
			user_list[message.author.id]
		));

		# Pre-set this
		wm_message = ""

		# For pre-programmed messages only.
		if affliction.strict_mode:
			message_content = message.content.lower()
			# Asking for help?
			if 'help' in message_content:
				help_text = '```'
				for i in self.responses.keys():
					help_text += f'{i.ljust(12)} ::: {self.responses[i]}\n'
				help_text += '```'
				await message.author.send(help_text)

			if message_content.strip() in self.responses.keys():
				wm_message = self.responses[message_content.strip()]

		else:
			wm_message = message.content

		# Delete old message
		await message.delete()

		if wm_message != "":
			# Send new message
			webhook = await get_or_make_webhook(message.guild, message.channel)
			await webhook.send(wm_message, username=message.author.display_name, avatar_url=message.author.display_avatar.url, silent=True)
