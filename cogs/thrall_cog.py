from discord.ext import tasks, commands
import optout
from discord import app_commands
import os
import discord
import time
import logging
#from random import randint
from random import choice
from random import randint
from typing import Literal
from helpers import is_bot
from typing import Optional
import guilds
from webhooks import get_or_make_webhook

# Rosa ID
rosa_id = 153857426813222912

THRALL_ENABLED_KEY = "thrall_enabled"

# Thrall role ID: 1125452920301834250
mantra_file_location = os.path.join(os.path.dirname(__file__),"..","resources","mantras.txt")

logger = logging.getLogger('bot.thrall')

class Thrall_Cog(commands.Cog):
	# List of mantras
	mantras = []

	def Thrall_Affliction(self,
		thrall_until = None,
		replace_chance: int = 100):
		return {
			"affliction_type": "thrall",
			"thrall_until": thrall_until or (time.time() + (3600*24*7*52)),
			"replace_chance": replace_chance
		}

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
			if guild["users"] is None:
				continue

			copy_of_users = dict(guild["users"]).items()
			for user_id,affliction_list in copy_of_users:
				afflictions = list(filter(
					lambda x: x["affliction_type"] == "thrall",
					affliction_list))

				# Get first, if exists
				if len(afflictions) == 0:
					continue
				affliction = afflictions[0]

				# Must pass time
				if time.time() < affliction["thrall_until"]:
					continue

				logger.info(f"Thralldom timeout on {user_id}")

				await guilds.unafflict_target(
					guild,
					self.bot,
					user_id,
					self.Thrall_Affliction()
					)

	# Thrall "leash"
	@app_commands.command(description='Toggle global thrall enabled')
	async def toggle_thrall_global(self, inter: discord.Interaction):
		# Prevent rosa from self-thralling
		#if await is_rosa(target):
		#	return
		bot_guild = guilds.bot_guilds[str(inter.guild.id)]

		new_setting = not bot_guild.get("settings").get(THRALL_ENABLED_KEY, True)

		bot_guild["settings"][THRALL_ENABLED_KEY] = new_setting

		await inter.response.send_message(f"global thrall setting is now {new_setting}",ephemeral=True)


	# Thrall "leash"
	@app_commands.command(description='Entrall the target')
	async def afflict_thrall(self, inter: discord.Interaction, target: discord.Member, clear: Optional[Literal["clear"]] = None):
		# Prevent rosa from self-thralling
		#if await is_rosa(target):
		#	return

		# Prevent bot from thralling itself
		if await is_bot(self.bot, target):
			return
		if optout.is_optout(target.id):
			await inter.response.send_message("User has opted out of bot.", ephemeral=True)
			return
		if inter.user.id == target.id and clear is None:
			await inter.response.send_message("You cannot use this command on yourself, thrall.")
			return

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		affliction = self.Thrall_Affliction(thrall_until=time.time()+(3600*24*7*52),replace_chance=100)

		logger.debug(f"Affliction request: user={target.display_name} thrall_until=900 replace_chance=100")

		if clear is None:
			# Afflict user
			await guilds.afflict_target(bot_guild, self.bot, target, affliction)
			await inter.response.send_message(f"Successfully afflicted {target.name}.", ephemeral=True)

		else:
			# Afflict user
			await guilds.unafflict_target(bot_guild, self.bot, target, affliction)
			await inter.response.send_message(f"Successfully cleared afflicted {target.name}.", ephemeral=True)

	# Unthrall all thralls
	@app_commands.command(description='Warning: time-intensive process. May time out before responding!')
	async def enthrall_remove_all(self, inter: discord.Interaction):

		# Filter list by thralls
		# Remove thralldom from all thralls

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		thrall_list = 'Removing:\n'
		if bot_guild["users"] is None:
			return
		
		bot_guild_users_copy = bot_guild["users"].copy()

		for user_id,affliction_list in bot_guild_users_copy.items():
			afflictions = list(filter(
				lambda x: type(x) == self.Thrall_Affliction,
				affliction_list))

			# Get first, if exists
			if len(afflictions) == 0:
				continue
			#affliction = afflictions[0]

			await guilds.unafflict_target(
				self.bot,
				user_id,
				self.Thrall_Affliction()
				)
			thrall_list += f'- {user_id}\n'

		await inter.response.send_message(thrall_list, ephemeral=True)


	async def on_owner_mention(self, message):
		# Prevent rosa from self-thralling
		#if await is_rosa(message.author):
		#	return 

		# od exemption
		if message.author.id == 201821870255898625:
			return
			
		# Prevent bot from thralling itself
		if await is_bot(self.bot, message.author):
			return

		bot_guild = guilds.bot_guilds[str(message.guild.id)]

		# If the feature is turned off
		if not bot_guild["settings"].get(THRALL_ENABLED_KEY, True):
			return

		thrall_duration = 40

		affliction = self.Thrall_Affliction(thrall_until=time.time()+thrall_duration,replace_chance=100)

		logger.debug(f"Affliction request: user={message.author.display_name} thrall_until={thrall_duration} replace_chance=100")

		await guilds.afflict_target(bot_guild, self.bot, message.author, affliction)


	# Run message relay
	async def on_message(self, message):


		# Get user's affliction settings
		user_list = guilds.bot_guilds[str(message.guild.id)]["users"]
		# To get here, the user must already have the setting,
		# so we can almost guarantee it's in the list
		affliction = next(filter(
			lambda x: x["affliction_type"] == "thrall",
			user_list[message.author.id]
		))

		# Run chance
		if randint(0,99) > affliction["replace_chance"]:
			return

		wm_content = self.get_mantra().strip()
		await message.delete()
		webhook = await get_or_make_webhook(message.guild, message.channel)
		await webhook.send(
			wm_content,
			username=message.author.display_name,
			avatar_url=message.author.display_avatar.url,
			silent=True)

	# Modify messages
	def get_mantra(self):
		return choice(self.mantras)

async def setup(bot):
	await bot.add_cog(Thrall_Cog(bot))

