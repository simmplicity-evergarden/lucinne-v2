import shelve
import os
from typing import Optional,Literal,Union
from typing import get_args
import logging
import discord
from helpers import *

shelf_location = os.path.join("pickles","guilds.shelf")
shelf_location_optout = os.path.join("pickles","optout.shelf")
# Ensure pickles folder exists, create if it doesn't'
if not os.path.exists(os.path.dirname(shelf_location)):
	os.mkdir(os.path.dirname(shelf_location))

bot_guilds = shelve.open(shelf_location, writeback=True)
optouts = shelve.open(shelf_location_optout, writeback=True)

try:
	del optouts["352264281896517635"]
	print("Cleared test account optout")
except:
	pass

affliction_list = Literal["Robot","Feral","Squeak","Thrall","Object"]

logger = logging.getLogger('bot.guilds')

def add_guild(guild_id: [int,str]):
	bot_guilds[str(guild.id)] = new_guild(guild.id)
	logger.info(f"Joined the guild {guild.id} ({guild.name})")

def remove_guild(guild_id: [int,str]):
	if str(guild_id) in bot_guilds:
		del bot_guilds[str(guild_id)]
		logger.info(f"Left the guild {guild_id}")
	else:
		logger.warning(f"Left the guild {guild_id} - it was not in guilds list.")

def new_guild(guild_id: int): 
	return {
		"id":guild_id
		"admins":[],
		"roles": {},
		"users": {},
		"webhook_name": "",
		"settings": {},
		"leash_map": {}
	}

def get_or_make_guild(guild_id: Union[int,str,dict]):
	if guild_id not in bot_guilds:
		add_guild(guild_id)
	return bot_guilds[guild_id]

# Add affliction (and optionally role) to user
async def afflict_target(guild: [dict,int,str], bot, target: Union[discord.Member, discord.User, int], affliction):
	# convert to real user
	target = await find_member(bot, target, guild["id"])

	if type(guild) != "dict":
		guild = get_or_make_guild(guild)

	affliction_type = affliction["type"]

	# Add to internal list
	if target.id not in guild["users"]:
		# Add target to list
		guild["users"][target.id] = [affliction]
	else:
		# Remove pre-existing affliction from list, if any
		guild["users"][target.id] = list(filter(lambda x: type(x).__name__ != affliction_type, guild["users"][target.id])) + [affliction]
	logger.info(f"AFFLICTION: Added {affliction_type} to {target.name} in {guild["id"]}")

	# Role control
	affliction_role = guild["roles"].get(affliction_type.removesuffix("_Affliction").lower())
	if affliction_role is not None:
		await add_role(bot, affliction_role, target, guild["id"])
		logger.info(f"ROLE: Added {affliction_role} to {target.name} in {guild["id"]}")

async def unafflict_target(guild: dict, bot, target: Union[discord.Member, discord.User, int], affliction):
	# convert to real user
	target = await find_member(bot, target, guild["id"])

	if type(guild) != "dict":
		guild = get_or_make_guild(guild)


	affliction_type = affliction["type"]
	print(affliction_type)

	# Add to internal list
	if target.id not in guild["users"]
		# Add target to list
		pass
	else:
		# Remove pre-existing affliction from list, if any
		guild["users"][target.id] = list(filter(lambda x: type(x).__name__ != affliction_type, guild["users"][target.id]))
		# Remove empty users
		if len(guild["users"][target.id]) == 0:
			del guild["users"][target.id]


	logger.info(f"AFFLICTION: Removed {affliction_type} to {target.name} in {guild["id"]}")

	# Role control
	affliction_role = guild["roles"].get(affliction_type.removesuffix("_Affliction").lower())
	if affliction_role is not None:
		await remove_role(bot, affliction_role, target, guild["id"])
		logger.info(f"ROLE: Removed {affliction_role} from {target.name} in {guild["id"]}")

async def clear_target(guild: dict, bot, target: Union[discord.Member, discord.User, int]):
	# convert to real user
	target = await find_member(bot, target, guild["id"])

	if type(guild) != "dict":
		guild = get_or_make_guild(guild)

	# Add to internal list
	if target.id not in guild["users"]:
		# Add target to list
		pass
	else:
		# Remove pre-existing affliction from list, if any
		del guild["users"][target.id]
		logger.info(f"Cleared all afflictions from {target.name}")

	for role in get_args(affliction_list):
		if role.lower() in guild["roles"]:
			if await has_role(bot, guild["roles"].get(role.removesuffix("_Affliction").lower()), target, guild["id"]):
				affliction_role = guild["roles"].get(role.removesuffix("_Affliction").lower())
				await remove_role(bot, affliction_role, target, guild["id"])
				logger.info(f"ROLE: Removed {affliction_role} from {target.name} in {guild["id"]}")
