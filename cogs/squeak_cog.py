from discord.ext import tasks, commands
from discord import app_commands
from discord import ui
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

logger = logging.getLogger('bot.feral')

class Squeak_Cog(commands.Cog):
	class Squeak_Affliction():
		smile_required: bool = None
		word_squeak_chance: int = None
		msg_squeak_chance: int = None

		def __init__(self,
			smile_required = None,
			word_squeak_chance = None,
			msg_squeak_chance = None,
			reference = None):

			# Use reference as base
			if reference is not None:
				self.smile_required = reference.smile_required
				self.word_squeak_chance = reference.word_squeak_chance
				self.msg_squeak_chance = reference.msg_squeak_chance

			# Priority: updated value, reference value, or [default]
			self.smile_required = smile_required or self.smile_required or False
			self.word_squeak_chance = word_squeak_chance or self.word_squeak_chance or 0
			self.msg_squeak_chance = msg_squeak_chance or self.msg_squeak_chance or 0

			# If all three are down, ultimate default
			if not self.smile_required and self.word_squeak_chance == 0 and self.msg_squeak_chance == 0:
				self.word_squeak_chance = 10


	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Squeak_Cog')

	@app_commands.command(description='Afflict inflatable on target')
	@app_commands.describe(target = "affliction to assign a role to")
	@app_commands.describe(word_squeak_chance = "chance of a word being replaced with squeak sounds")
	@app_commands.describe(msg_squeak_chance = "chance of a message being replaced with squeak sounds")
	@app_commands.describe(smile_required = "requires the user to **Smile!~**")
	@app_commands.describe(clear = "use this to clear the assigned role; overrides other options")
	async def afflict_squeak(self,
		inter: discord.Interaction,
		target: discord.User,
		word_squeak_chance: Optional[app_commands.Range[int, 0]] = None,
		msg_squeak_chance: Optional[app_commands.Range[int, 0]] = None,
		smile_required: Optional[bool] = None,
		clear: Optional[Literal["clear"]] = None):

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		affliction = None
		if bot_guild.users.get(target.id, None) is not None:
			# Filter first
			affliction = list(filter(
				lambda x: type(x).__name__ == self.Squeak_Affliction.__name__,
				bot_guild.users[target.id]
			));
			# Get first, if exists
			if len(affliction) != 0:
				affliction = affliction[0]
			else:
				affliction = None


		affliction = self.Squeak_Affliction(smile_required, word_squeak_chance, msg_squeak_chance, reference=affliction)

		logger.debug(f"Affliction request: user={target.display_name} smile_required={smile_required} " +\
			f"word_squeak_chance={word_squeak_chance} msg_squeak_chance={msg_squeak_chance}")

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
			lambda x: type(x).__name__ == self.Squeak_Affliction.__name__,
			user_list[message.author.id]
		));

		# Allow Rosa sticker
		for sticker in message.stickers:
			if sticker.name == 'Rosaflatable':
				return

		# Preset this
		wm_content = None
		show_tease = False

		# Smile enforcer
		if affliction.smile_required and re.search(r"\*\*Smil(?:e(?:s)?|ing)!~\*\*",message.content) == None:
			# Tease on error, ~5% chance
			show_tease = randint(0,20) == 1
			# Replace message
			wm_content = squeak_message(message.content, chance=100)
		# Full sentence replacer
		elif randint(0,99) < affliction.msg_squeak_chance:
			wm_content = squeak_message(message.content, chance=100)
		else:
			wm_content = squeak_message(message.content, chance=affliction.word_squeak_chance)

		# Avoid unnecessary replacements or deletions.
		if wm_content == None or wm_content == message.content:
			return

		await message.delete()
		webhook = await get_or_make_webhook(message.guild, message.channel)
		webhook_msg = await webhook.send(
			wm_content,
			username=message.author.display_name,
			avatar_url=message.author.display_avatar.url,
			files=message.attachments,
			silent=True,
			wait=show_tease)

		if show_tease:
			# Tease on error, 5% chance
			await webhook_msg.reply("Someone forgot to **Smile!~**")



	# Run reaction relay
	async def on_reaction_add(self, reaction: discord.Reaction, member: discord.Member):
		# Get pre-existing affliction, if it exists
		affliction = None
		bot_guild = guilds.bot_guilds[str(reaction.message.guild_id)]
		if bot_guild.users.get(member.id, None) is not None:
			affliction = next(filter(
				lambda x: type(x).__name__ == self.Squeak_Affliction.__name__,
				bot_guild.users[member.id]
			));

		print(f"{reaction} {member}")

		# Set defaults
		smile_required, word_squeak_chance, msg_squeak_chance = (None,None,None)

		if reaction.emoji.name == 'Rosasmile':
			smile_required = True
		elif reaction.emoji == '🎈': # Balloon
			word_squeak_chance = 10
		else: # Speech bubble
			msg_squeak_chance = 10

		# Create new affliction
		affliction = self.Squeak_Affliction(smile_required, word_squeak_chance, msg_squeak_chance, reference=affliction)

		logger.debug(f"Affliction request: user={member.display_name} smile_required={smile_required} " +\
			f"word_squeak_chance={word_squeak_chance} msg_squeak_chance={msg_squeak_chance}")

		# Afflict user
		await bot_guild.afflict_target(self.bot, member, affliction)


def squeak_message(message, chance=0) -> str:
	new_message = ""
	for word in message.split():
		if randint(0,100) < chance:
			new_message += f" {squeak_word(word)}"
		else:
			new_message += f" {word}"

	return new_message.strip()

def squeak_word(word) -> str:
	if len(word) == 0:
		return '';
	elif len(word) < 3:
		return 'sqk'
	elif len(word) < 5:
		return 'SQUEAK'
	else:
		match randint(0,6):
			case 0:
				return 's'+str('q'*(len(word)-1))+'rk'
			case 1:
				return 'squ'+str('i'*(len(word)-1))+'rk'
			case 2:
				return 'squ'+str('i'*(len(word)-1))+'sh'
			case 3:
				return 'fw'+str('o'*(len(word)-1))+'mp'
			case 4:
				return 'fw'+str('w'*(len(word)-1))+'mp'
			case 5:
				return 'cr'+str('e'*(len(word)-1))+'ak'
			case 6:
				return '**Smile!**'
			case 7:
				return 'Rosa'
