from discord.ext import tasks, commands
from discord import app_commands
from discord import ui
#import re
import os
import discord
import logging
#from random import randint
from random import randint
from random import choices
from random import choice
from typing import Literal
from typing import Optional
import guilds
from cogs.squeak_censor_cog import censor_message
from webhooks import get_or_make_webhook
import re
# File to get the message texts from
responses_file_location = os.path.join(os.path.dirname(__file__),"..","resources","robot_messages.txt")
paw_pics_prefix = os.path.join(os.path.dirname(__file__),'..','resources','paws')


logger = logging.getLogger('bot.feral')

class Feral_Cog(commands.Cog):
	class Feral_Affliction():
		vote_requirement: int = 0
		base_huff_chance: int = 0


		def __init__(self,
			vote_requirement = None,
			base_huff_chance = None,
			reference = None):

			# Use reference as base
			if reference is not None:
				self.vote_requirement = reference.vote_requirement
				self.base_huff_chance = reference.base_huff_chance

			# Priority: updated value, reference value, or [default]
			self.vote_requirement = vote_requirement or self.vote_requirement or 3
			self.base_huff_chance = base_huff_chance or self.base_huff_chance or 10


	class Feral_Message():
		user_id: int = 0
		# original message
		message: str = ""
		vote_score = 0
		# Store these at creation time for easier use later
		vote_requirement = 0
		huff_chance = 0

		def __init__(self,
			user_id: int,
			message: str,
			vote_requirement: int,
			huff_chance: int):

			self.user_id = user_id
			self.message = message
			self.vote_requirement = vote_requirement
			self.huff_chance = huff_chance
			self.vote_score = 0

	message_saving_dict = {}
	paw_pics = []

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Feral_Cog')

		# Get list of paw pics
		for filename in os.listdir(paw_pics_prefix):
			self.paw_pics.append(os.path.join(paw_pics_prefix, filename))


	@app_commands.command(description='Afflict feral on target')
	@app_commands.describe(target = "affliction to assign a role to")
	@app_commands.describe(vote_requirement = "required unlock votes")
	@app_commands.describe(base_huff_chance = "chance/100 of huffing paws")
	@app_commands.describe(clear = "use this to clear the assigned role; overrides other options")
	async def afflict_feral(self,
		inter: discord.Interaction,
		target: discord.User,
		vote_requirement: Optional[app_commands.Range[int, 0]] = 3,
		base_huff_chance: Optional[app_commands.Range[int, 0]] = 3,
		clear: Optional[Literal["clear"]] = None):

		if inter.user.id == target.id:
			await inter.response.send_message("You cannot use this command on yourself, pawslut.")
			return

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		affliction = None
		if bot_guild.users.get(target.id, None) is not None:
			# Filter first
			affliction = list(filter(
				lambda x: type(x).__name__ == self.Feral_Affliction.__name__,
				bot_guild.users[target.id]
			));
			# Get first, if exists
			if len(affliction) != 0:
				affliction = affliction[0]
			else:
				affliction = None

		affliction = self.Feral_Affliction(vote_requirement, base_huff_chance, reference=affliction)

		logger.debug(f"Affliction request: user={target.display_name} vote_requirement={vote_requirement} base_huff_chance={base_huff_chance}")

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
		affliction: self.Feral_Affliction = next(filter(
			lambda x: type(x).__name__ == self.Feral_Affliction.__name__,
			user_list[message.author.id]
		));

		# Pre-set these
		wm_content = None
		wm_files = []

		# If there are images in message
		if len(message.attachments) > 0:
			# Replace images
			for attachment in message.attachments:
				if 'image' in attachment.content_type:
					wm_files.append(discord.File(choice(self.paw_pics)))
					print('image!')

		# If there is any text in the message
		wm_content = message_modifier(message.content)

		await message.delete()
		webhook = await get_or_make_webhook(message.guild, message.channel)

		last_message_webhook_msg = await webhook.send(
			wm_content,
			username=message.author.display_name,
			avatar_url=message.author.display_avatar.url,
			files=wm_files,
			silent=True,
			wait=True)

		if wm_content != '':
			await last_message_webhook_msg.add_reaction('🔓')
			await last_message_webhook_msg.add_reaction('🔒')
			await last_message_webhook_msg.add_reaction('🐾')

			# Save author ID and message content
			self.message_saving_dict[last_message_webhook_msg.id] = \
				self.Feral_Message(
					message.author.id,
					censor_message(message.content),
					affliction.vote_requirement,
					affliction.base_huff_chance
					)
			#self.message_saving_dict[last_message_webhook_msg.id] = (message.author.id, message.content)


	# Run message relay
	async def on_reaction_add(self, reaction: discord.Reaction, member: discord.Member, negative=False):
		# only affect messages in dict
		reaction_message = self.message_saving_dict.get(reaction.message.id, None)

		print(f"{reaction} {member} {negative}")

		# return if message isn't found
		if reaction_message is None:
			return

		# return if owner's ID
		if member.id == reaction_message.user_id:
			return

		if member.id in guilds.bot_guilds[str(reaction.message.guild.id)].admins:
			admin_modifier = 100
		else:
			admin_modifier = 1

		if negative:
			negative_modifier = -1
		else:
			negative_modifier = 1

		# Determine what to do
		match reaction.emoji:
			case '🔓': # Unlock
				reaction_message.vote_score += 1 * negative_modifier
			case '🔒': # Lock
				reaction_message.vote_score -= 1 * admin_modifier * negative_modifier
			case '🐾': # Paw
				reaction_message.huff_chance += 5 * negative_modifier
			case '🔑': # Key
				reaction_message.vote_score += (admin_modifier - 1) * negative_modifier
				reaction_message.huff_chance -= 200 * negative_modifier

		#logger.debug(f"Feral message {reaction.message.id} now has vote={reaction_message.vote_score} huff={reaction_message.huff_chance}")

		# Scoring and replacing
		if reaction_message.vote_score >= reaction_message.vote_requirement:

			#logger.debug(f"Feral message {reaction.message.id} now has vote={reaction_message.vote_score} huff={reaction_message.huff_chance}")
			# Get webhook
			webhook = await get_or_make_webhook(reaction.message.guild, reaction.message.channel)

			# Huff chance
			dice_roll = randint(0,100)
			print(dice_roll)
			print(reaction_message.huff_chance)
			print(dice_roll < reaction_message.huff_chance)
			if dice_roll < reaction_message.huff_chance:
				reaction_message.message = "***HUFFS PAWS HUFFS PAWS*** **AWOOO~**"

			# double-check this because I think it's fucking with the API limits
			# only affect messages in dict
			reaction_message = self.message_saving_dict.get(reaction.message.id, None)
			# return if message isn't found
			if reaction.message.id is None:
				return

			await webhook.edit_message(reaction.message.id, content=reaction_message.message)
			self.message_saving_dict.pop(reaction.message.id)


	# Use the same code, but inverted
	async def on_reaction_remove(self, reaction: discord.Reaction, member: discord.Member):
		await self.on_reaction_add(reaction, member, negative=True)


def message_modifier(message: str) -> str:
	if message.endswith('...'):
		message = "*whines*"
	elif message.endswith('!'):
		message = "***bark!***"
	else:
		message = re.sub(r"(?:(?<![<:@])\b[\w']*\w*|(?:<a?)?:\w+:(?:\d{18,19}>)?)",woof_length,message)
	return message

def woof_length(word):
	if len(word.group()) == 0:
		return '';
	elif len(word.group()) < 3:
		match randint(0,1):
			case 0:
				return 'gr'
			case 1:
				return 'arf'
			case 2:
				return 'ru'
	elif len(word.group()) < 5:
		match randint(0,1):
			case 0:
				return 'ruff'
			case 1:
				return 'woof'
			case 2:
				return 'bark'
	elif len(word.group()) > 10:
		return 'aw'+str('o'*(len(word.group())))
	else:
		match randint(0,7):
			case 0:
				return 'ba'+str('r'*(len(word.group())-1))+'k'
			case 1:
				return 'w'+str('o'*(len(word.group())-1))+'f'
			case 2:
				return 'ba'+str('r'*(len(word.group())-1))+'k'
			case 3:
				return 'b'+str('a'*(len(word.group())//2))+str('r'*(len(word.group())//2))+'k'
			case 4:
				return '*whimper*'
			case 5:
				return 'aww'+str('o'*(len(word.group())-1))
			case 6:
				return '*growl*'
			case 7:
				return '*pants*'


async def setup(bot):
	await bot.add_cog(Feral_Cog(bot))

