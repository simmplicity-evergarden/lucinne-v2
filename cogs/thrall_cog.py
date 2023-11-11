from discord.ext import tasks, commands
from discord import app_commands
import pickle
import re
import os
import discord
import time
import logging
from string import ascii_uppercase
#from random import randint
from random import choice
from random import randint
from typing import Literal
from helpers import *
from typing import Optional
import guilds
from webhooks import get_or_make_webhook

# Rosa ID
rosa_id = 153857426813222912


# Thrall role ID: 1125452920301834250


mantra_file_location = os.path.join(os.path.dirname(__file__),"..","resources","mantras.txt")

logger = logging.getLogger('bot.thrall')

class Thrall_Cog(commands.Cog):
	# List of mantras
	mantras = []

	class Thrall_Affliction():
		thrall_until: int = 0
		replace_chance: int = 0

		def __init__(self,
			thrall_until = None,
			replace_chance = None):

			# Priority: updated value or [default]
			self.thrall_until = thrall_until or (time.time() + (3600*24*7*52))
			self.replace_chance = replace_chance or 100

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded Thrall_Cog')
		# Load mantras
		if os.path.exists(mantra_file_location):
			with open(mantra_file_location, 'r') as mantra_file:
				self.mantras = mantra_file.readlines()
		# Start loop for clearing thralls
		self.clean_thralls.start()

	#async def cog_load(self):


	async def cog_unload(self):
		self.clean_thralls.unload()

	# Remove thralldom after a user's timer expires
	@tasks.loop(seconds=20)
	async def clean_thralls(self):

		# For guild in guild list
		for guild in guilds.bot_guilds.values():
			if guild.users is None:
				continue
			for user_id,affliction_list in guild.users.items():
				afflictions = list(filter(
					lambda x: type(x) == self.Thrall_Affliction,
					affliction_list))

				# Get first, if exists
				if len(afflictions) == 0:
					continue
				affliction = afflictions[0]

				# Must pass time
				if time.time() < affliction.thrall_until:
					continue

				logger.info(f"Thralldom timeout on {user_id}")

				await guild.unafflict_target(
					self.bot,
					user_id,
					self.Thrall_Affliction()
					)


	# Thrall "leash"
	@app_commands.command(description='Entrall the target')
	async def afflict_thrall(self, inter: discord.Interaction, target: discord.Member, clear: Optional[Literal["clear"]] = None):
		# Prevent rosa from self-thralling
		if await is_rosa(target):
			return

		# Prevent bot from thralling itself
		if await is_bot(self.bot, target):
			return

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		affliction = self.Thrall_Affliction(thrall_until=time.time()+(3600*24*7*52),replace_chance=100)

		logger.debug(f"Affliction request: user={target.display_name} thrall_until=900 replace_chance=100")

		if clear is None:
			# Afflict user
			await bot_guild.afflict_target(self.bot, target, affliction)
			await inter.response.send_message(f"Successfully afflicted {target.name}.", ephemeral=True)

		else:
			# Afflict user
			await bot_guild.unafflict_target(self.bot, target, affliction)
			await inter.response.send_message(f"Successfully cleared afflicted {target.name}.", ephemeral=True)

	# Unthrall all thralls
	@app_commands.command(description='Warning: time-intensive process. May time out before responding!')
	async def enthrall_remove_all(self, inter: discord.Interaction):

		# Filter list by thralls
		# Remove thralldom from all thralls

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		thrall_list = 'Removing:\n'
		if bot_guild.users is None:
			return
		for user_id,affliction_list in bot_guild.users.items():
			afflictions = list(filter(
				lambda x: type(x) == self.Thrall_Affliction,
				affliction_list))

			# Get first, if exists
			if len(affliction) == 0:
				continue
			affliction = affliction[0]

			# Must pass time
			if time.time() < affliction.thrall_until:
				continue

			await bot_guild.unafflict_target(
				self.bot,
				user_id,
				self.Thrall_Affliction()
				)
			thrall_list += f'- {member_obj.mention}\n'

		await inter.response.send_message(thrall_list, ephemeral=True)


	async def on_owner_mention(self, message):
		# Prevent rosa from self-thralling
		if await is_rosa(message.author):
			return

		# Prevent bot from thralling itself
		if await is_bot(self.bot, message.author):
			return

		bot_guild = guilds.bot_guilds[str(message.guild.id)]

		thrall_duration = 40

		affliction = self.Thrall_Affliction(thrall_until=time.time()+thrall_duration,replace_chance=100)

		logger.debug(f"Affliction request: user={message.author.display_name} thrall_until={thrall_duration} replace_chance=100")

		await bot_guild.afflict_target(self.bot, message.author, affliction)


	# Run message relay
	async def on_message(self, message):


		print("yolo")

		# Get user's affliction settings
		user_list = guilds.bot_guilds[str(message.guild.id)].users
		# To get here, the user must already have the setting,
		# so we can almost guarantee it's in the list
		affliction = next(filter(
			lambda x: type(x).__name__ == self.Thrall_Affliction.__name__,
			user_list[message.author.id]
		));

		# Run chance
		if randint(0,99) > affliction.replace_chance:
			return

		wm_content = self.get_mantra()

		print(wm_content)

		await message.delete()
		webhook = await get_or_make_webhook(message.guild, message.channel)
		webhook_msg = await webhook.send(
			wm_content,
			username=message.author.display_name,
			avatar_url=message.author.display_avatar.url,
			silent=True)

	# Modify messages
	def get_mantra(self):
		return choice(self.mantras)
