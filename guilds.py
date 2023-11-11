import shelve
import os
from typing import Optional
from typing import Literal
from typing import get_args
import logging
import discord
from helpers import *

shelf_location = os.path.join("pickles","guilds.shelf")
# Ensure pickles folder exists, create if it doesn't'
if not os.path.exists(os.path.dirname(shelf_location)):
	os.mkdir(os.path.dirname(shelf_location))

bot_guilds = shelve.open(shelf_location, writeback=True)


affliction_list = Literal["Robot","Feral","Squeak","Thrall"]

logger = logging.getLogger('bot.guilds')

def add_guild(guild: discord.Guild):
	bot_guilds[str(guild.id)] = Bot_Guild(guild.id)
	logger.info(f"Joined the guild {guild.id} ({guild.name})")

def remove_guild(guild):
	if str(guild.id) in bot_guilds:
		del bot_guilds[str(guild.id)]
		logger.info(f"Left the guild {guild.id} ({guild.name})")
	else:
		logger.warning(f"Left the guild {guild.id} ({guild.name}) - it was not in guilds list.")

class Bot_Guild:
	guild_id: int = 0
	# User IDs who are considered "admins"
	admins: list[int] = []
	# User IDs who cannot be affected by the bot
	exempt: list[int] = []
	# Mapping of internal role names to IDs
	roles: dict[str, int] = {}
	# Mapping of user IDs to afflictions
	users = {}
	# Webhook for the server
	webhook_name: str = ""

	# leash_holder_id : (last_channel_id, list[discord.Member])
	leash_map = {}

	def __init__(self, guild_id: int):
		self.guild_id = guild_id
		# User IDs who are considered "admins"
		self.admins = []
		# User IDs who cannot be affected by the bot
		self.exempt = []
		# Mapping of internal role names to IDs
		self.roles = {}
		# Mapping of user IDs to list of afflictions
		self.users = {}
		self.webhook_name = ""
		# Mapping of user IDs to leashed users
		self.leash_map = {}

	# Add affliction (and optionally role) to user
	async def afflict_target(self, bot, target: Union[discord.Member, discord.User, int], affliction):
		# convert to real user
		target = await find_member(bot, target, self.guild_id)

		affliction_type = type(affliction).__name__

		# Add to internal list
		if target.id not in self.users:
			# Add target to list
			self.users[target.id] = [affliction]
		else:
			# Remove pre-existing affliction from list, if any
			self.users[target.id] = list(filter(lambda x: type(x).__name__ != affliction_type, self.users[target.id])) + [affliction]
		logger.info(f"AFFLICTION: Added {affliction_type} to {target.name} in {self.guild_id}")

		# Role control
		affliction_role = self.roles.get(affliction_type.removesuffix("_Affliction").lower())
		if affliction_role is not None:
			await add_role(bot, affliction_role, target, self.guild_id)
			logger.info(f"ROLE: Added {affliction_role} to {target.name} in {self.guild_id}")

	async def unafflict_target(self, bot, target: Union[discord.Member, discord.User, int], affliction):
		# convert to real user
		target = await find_member(bot, target, self.guild_id)

		affliction_type = type(affliction).__name__
		print(affliction_type)

		# Add to internal list
		if target.id not in self.users:
			# Add target to list
			pass
		else:
			# Remove pre-existing affliction from list, if any
			self.users[target.id] = list(filter(lambda x: type(x).__name__ != affliction_type, self.users[target.id]))

		logger.info(f"AFFLICTION: Removed {affliction_type} to {target.name} in {self.guild_id}")

		# Role control
		affliction_role = self.roles.get(affliction_type.removesuffix("_Affliction").lower())
		if affliction_role is not None:
			await remove_role(bot, affliction_role, target, self.guild_id)
			logger.info(f"ROLE: Removed {affliction_role} from {target.name} in {self.guild_id}")

	async def clear_target(self, bot, target: Union[discord.Member, discord.User, int]):
		# convert to real user
		target = await find_member(bot, target, self.guild_id)

		print("yolyolo")

		# Add to internal list
		if target.id not in self.users:
			# Add target to list
			pass
		else:
			# Remove pre-existing affliction from list, if any
			self.users[target.id] = []
			logger.info(f"Cleared all afflictions from {target.name}")

		for role in get_args(affliction_list):
			if role.lower() in self.roles:
				if await has_role(bot, self.roles.get(role.removesuffix("_Affliction").lower()), target, self.guild_id):
					affliction_role = self.roles.get(role.removesuffix("_Affliction").lower())
					await remove_role(bot, affliction_role, target, self.guild_id)
					logger.info(f"ROLE: Removed {affliction_role} from {target.name} in {self.guild_id}")
