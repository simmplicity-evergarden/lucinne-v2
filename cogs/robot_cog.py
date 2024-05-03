from discord.ext import commands
import optout
from discord import app_commands
from cogs.squeak_censor_cog import censor_message
import os
import discord
import logging
import re
from typing import Literal
from typing import Optional
import guilds
from webhooks import get_or_make_webhook

# Regex objects - match spaces and dashes
REGEX_PATTERN = re.compile("((?: |-)+)")
REPLACE_PATTERN = re.compile("\1\1\1")

# Folder to get the message texts from
responses_folder_location = os.path.join(os.path.dirname(__file__),"..","resources")
responses_type_list = ["robot","doll","emoji"]


logger = logging.getLogger('bot.robot')

class Robot_Cog(commands.Cog):
	def Robot_Affliction(self,
		pre_message_dict: str = None,
		max_charge: int = None):
		return {
			"affliction_type": "robot",
			"pre_message_dict": pre_message_dict,
			"max_charge": max_charge,
			"current_charge": max_charge,
		}

	# message_id: int -> user_id: int
	# used to track who to charge on key/battery reactions
	message_saving_dict = {}
	
	# type: str -> { keyword: str -> message: str  }
	pre_messages = {}

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Robot_Cog')
		
		for pre_message_type in responses_type_list:
			# Create sub-dict for message type
			self.pre_messages[pre_message_type] = {}
			responses_file_location = os.path.join(responses_folder_location, f"{pre_message_type}_responses.csv")
			if os.path.exists(responses_file_location):
				# Load messages
				with open(responses_file_location, 'r') as responses_file:
					for line in responses_file.readlines():
						# Add responses to dict
						response_item = line.split(',',1)
						if len(response_item) < 2:
							continue
						self.pre_messages[pre_message_type][response_item[0]] = response_item[1].strip()
				logger.debug(f"Loaded {len(self.pre_messages[pre_message_type])} {pre_message_type} responses from file")
			else:
				logger.warning(f"Error loading {pre_message_type} responses from file")

	@app_commands.command(description='Afflict robot on target')
	@app_commands.describe(target = "affliction to assign a role to")
	@app_commands.describe(dictionary = "predefined message list to use")
	@app_commands.describe(max_charge = "maximum words w/o recharge")
	@app_commands.describe(clear = "use this to clear the assigned role; overrides other options")
	async def afflict_robot(self,
						inter: discord.Interaction,
						target: discord.User,
						dictionary: Optional[Literal[tuple(responses_type_list)]] = None,
						max_charge: Optional[app_commands.Range[int, 0]] = None,
						clear: Optional[Literal["clear"]] = None):
		if optout.is_optout(target.id):
			await inter.response.send_message("User has opted out of bot.", ephemeral=True)
			return

		if inter.user.id == target.id:
			await inter.response.send_message("You cannot use this command on yourself, toy.")
			return


		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		affliction = self.Robot_Affliction(pre_message_dict = dictionary, max_charge = max_charge)

		logger.debug(f"Affliction request: user={target.display_name} dict={dictionary} max_charge={max_charge}")

		if clear is None:
			# Afflict user
			await guilds.afflict_target(bot_guild, self.bot, target, affliction)
			await inter.response.send_message(f"Successfully afflicted {target.name}.", ephemeral=True)

		else:
			# Afflict user
			await guilds.unafflict_target(bot_guild, self.bot, target, affliction)
			await inter.response.send_message(f"Successfully cleared afflicted {target.name}.", ephemeral=True)


	# Run message relay
	async def on_message(self, message):

		# Allow stickers
		for sticker in message.stickers:
			return

		# Get user's affliction settings
		user_list = guilds.bot_guilds[str(message.guild.id)]["users"]
		# To get here, the user must already have the setting,
		# so we can almost guarantee it's in the list
		affliction = next(filter(
			lambda x: x["affliction_type"] == "robot",
			user_list[message.author.id]
		))

		# Pre-set these
		wm_message = message.content
		wm_files = []
		for attach in message.attachments:
			wm_files.append(await attach.to_file())

		# For pre-programmed messages only.
		if affliction["pre_message_dict"] is not None:
			message_content = message.content.lower()
			# Asking for help?
			if 'help' in message_content:
				help_text = '```'
				for i in self.pre_messages[affliction["pre_message_dict"]].keys():
					help_text += f'{i.ljust(12)} ::: {self.pre_messages[affliction["pre_message_dict"]][i]}\n'
				help_text += '```'
				await message.author.send(help_text)

			if message_content.strip() in self.pre_messages[affliction["pre_message_dict"]].keys():
				wm_message = self.pre_messages[affliction["pre_message_dict"]][message_content.strip()]
			else:
				wm_message = ""


			wm_message = await self.bot.get_cog("Emoji_Fix_Cog").emoji_fix(wm_message)
		else:
			wm_message = censor_message(message.content)
			wm_message = await self.bot.get_cog("Emoji_Fix_Cog").emoji_fix(wm_message)

		# Charge logic
		if affliction["max_charge"] is not None:


			# If zero charge
			if affliction["current_charge"] < 1:
				# Fix any sub-zero value
				affliction["current_charge"] = 0

				# Message/attachments are gone
				wm_message = "....."
				wm_files = [] 
			
			# If non-zero charge, calculate cost
			else:
				# Count number of spaces or dashes
				# subtract that number
				affliction["current_charge"] -= len(re.findall(REGEX_PATTERN, wm_message))
				

			# If very low charge ( under 16% of max )
			if affliction["current_charge"] < ( affliction["max_charge"] // 6):
				# Slow message
				wm_message = re.sub(REGEX_PATTERN, r"\1\1\1\1", wm_message)
				# Limit to one attachment
				if len(wm_files) > 0:
					wm_files = [wm_files[0]]
			# If low charge ( under 33% of max )
			elif affliction["current_charge"] < ( affliction["max_charge"] // 3):
				# Slow message
				wm_message = re.sub(REGEX_PATTERN, r"\1\1", wm_message)
				# Limit to one attachment
				if len(wm_files) > 0:
					wm_files = [wm_files[0]]



		# Delete old message
		await message.delete()

		if wm_message != "" or wm_files != []:
			# Send new message
			webhook = await get_or_make_webhook(message.guild, message.channel)
			last_webhook_message = await webhook.send(
				wm_message, 
				username=message.author.display_name, 
				avatar_url=message.author.display_avatar.url, 
				files=wm_files,
				silent=True,
				wait=True)

			# Record author ID for later
			self.message_saving_dict[last_webhook_message.id] = message.author.id

	# Run message relay
	async def on_reaction_add(self, reaction: discord.Reaction, member: discord.Member):
		# only affect messages in dict
		message_user_id = self.message_saving_dict.get(reaction.message.id, None)

		# return if message isn't found
		if message_user_id is None:
			return

		# return if owner's ID, no self-charge
		if member.id == message_user_id:
			return

		# Other bots/dolls cannot add charge
		user_list = guilds.bot_guilds[str(reaction.message.guild.id)]["users"]
		if member.id in guilds.bot_guilds[str(reaction.message.guild.id)]["users"]:
			if any(map(
				lambda x: x["affliction_type"] == "robot",
				user_list[member.id]
				)):
				return 

		self.add_charge(reaction.message.guild.id, message_user_id, 25)
		
		"""
		try:
			# We should only get here if it was a valid emoji, so add charge
			add_charge(reaction.message.guild.id, message_user_id, 25)
			logger.debug(f"{member.name} charged user_id {message_user_id}")
		except:
			logger.warning(f"{member.name} could not charge user_id {message_user_id} because they are not a bot")
		"""




	# add charge to a user points% of max charge
	def add_charge(self, guild_id: int, user_id: int, points: int):
		# Get user's affliction settings
		user_list = guilds.bot_guilds[str(guild_id)]["users"]
		# To get here, the user must already have the setting,
		# so we can almost guarantee it's in the list
		affliction = next(filter(
			lambda x: x["affliction_type"] == "robot",
			user_list[user_id]
		))

		if affliction["max_charge"] is None:
			return

		affliction["current_charge"] = min(
			affliction["max_charge"],
			affliction["current_charge"] + int(affliction["max_charge"] * (points/100))
			)

async def setup(bot):
	await bot.add_cog(Robot_Cog(bot))

