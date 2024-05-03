from discord.ext import commands
import optout
from discord import app_commands
from cogs.squeak_censor_cog import censor_message
import re
import discord
import logging
#from random import randint
from random import randint
from typing import Literal
from typing import Optional
import guilds
from webhooks import get_or_make_webhook
# File to get the message texts from

logger = logging.getLogger('bot.squeak')

# This is needed for squeaking words properly, unfortunately.
CURRENT_SQUEAK_CHANCE = 0


class Squeak_Cog(commands.Cog):
	def Squeak_Affliction(self,
		smile_required = False,
		word_squeak_chance = 0,
		msg_squeak_chance = 0):
		return {
			"affliction_type": "squeak",
			"smile_required": smile_required or False,
			"word_squeak_chance": word_squeak_chance or 0,
			"msg_squeak_chance": msg_squeak_chance or 0
		}
	
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
		if optout.is_optout(target.id):
			await inter.response.send_message("User has opted out of bot.", ephemeral=True)
			return
		if inter.user.id == target.id:
			await inter.response.send_message("You cannot use this command on yourself, squeaky toy.")
			return

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		affliction = None
		if bot_guild["users"].get(target.id, None) is not None:
			# Filter first
			affliction = list(filter(
				lambda x: x["affliction_type"] == "squeak",
				bot_guild["users"][target.id]
			))
			# Get first, if exists
			if len(affliction) != 0:
				affliction = affliction[0]
			else:
				affliction = None


		affliction = self.Squeak_Affliction(smile_required, word_squeak_chance, msg_squeak_chance)

		logger.debug(f"Affliction request: user={target.display_name} smile_required={smile_required} " +\
			f"word_squeak_chance={word_squeak_chance} msg_squeak_chance={msg_squeak_chance}")

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

		# Get user's affliction settings
		user_list = guilds.bot_guilds[str(message.guild.id)]["users"]
		# To get here, the user must already have the setting,
		# so we can almost guarantee it's in the list
		affliction = next(filter(
			lambda x: x["affliction_type"] == "squeak",
			user_list[message.author.id]
		))

		# Allow Rosa sticker
		for sticker in message.stickers:
			if sticker.name == 'Rosaflatable':
				return

		# Preset this
		wm_content = None
		show_tease = False
		wm_files = []
		for attach in message.attachments:
			wm_files.append(await attach.to_file())


		# Smile enforcer
		if affliction["smile_required"] and re.search(r"\*\*Smil(?:e(?:s)?|ing)!~\*\*",censor_message(message.content)) is None:
			# Tease on error, ~5% chance
			show_tease = randint(0,20) == 1
			# Replace message
			wm_content = squeak_message(censor_message(message.content), chance=100)
		# Full sentence replacer
		elif randint(0,99) < affliction["msg_squeak_chance"]:
			wm_content = squeak_message(censor_message(message.content), chance=100)
		else:
			wm_content = squeak_message(censor_message(message.content), chance=affliction["word_squeak_chance"])

		# Avoid unnecessary replacements or deletions.
		if wm_content is None or wm_content.strip() == message.content.strip():
			return

		wm_content = await self.bot.get_cog("Emoji_Fix_Cog").emoji_fix(wm_content)

		await message.delete()
		webhook = await get_or_make_webhook(message.guild, message.channel)
		webhook_msg = await webhook.send(
			wm_content,
			username=message.author.display_name,
			avatar_url=message.author.display_avatar.url,
			files=wm_files,
			silent=True,
			wait=show_tease)

		if show_tease:
			# Tease on error, 5% chance
			await webhook_msg.reply("Someone forgot to **Smile!~**")



	# Run reaction relay
	async def on_reaction_add(self, reaction: discord.Reaction, member: discord.Member):
		# Get pre-existing affliction, if it exists
		affliction = None
		bot_guild = guilds.bot_guilds[str(reaction.message.guild.id)]
		if bot_guild["users"].get(member.id, None) is not None:
			affliction = next(filter(
				lambda x: x["affliction_type"] == "squeak",
				bot_guild["users"][member.id]
			))

		print("")

		# Set defaults
		smile_required, word_squeak_chance, msg_squeak_chance = (None,None,None)

		if not isinstance(reaction.emoji, str) and reaction.emoji.name == 'Rosasmile':
			smile_required = True
		elif reaction.emoji == '🎈': # Balloon
			word_squeak_chance = 7
		else: # Speech bubble
			msg_squeak_chance = 10

		# Create new affliction
		affliction = self.Squeak_Affliction(smile_required, word_squeak_chance, msg_squeak_chance)

		logger.debug(f"Affliction request: user={member.display_name} smile_required={smile_required} " +\
			f"word_squeak_chance={word_squeak_chance} msg_squeak_chance={msg_squeak_chance}")

		# Afflict user
		await guilds.afflict_target(bot_guild, self.bot, member, affliction)


# This is still here from a previous version of the bot
def squeak_message(message, chance=0) -> str:
	# since re.sub doesn't allow passing things
	global CURRENT_SQUEAK_CHANCE
	CURRENT_SQUEAK_CHANCE = chance
	return re.sub(r"(?:(?<![<:@])\b[\w']*\w*|(?:<a?)?:\w+:(?:\d{18,19}>)?)", squeak_word, message)
	new_message = ""
	for word in message.split():
		if randint(0,100) < chance:
			new_message += f" {squeak_word(word)}"
		else:
			new_message += f" {word}"

	return new_message.strip()

def squeak_word(word) -> str:
	if randint(0,100) > CURRENT_SQUEAK_CHANCE:
		return word.group()
	if len(word.group()) == 0:
		return ''
	elif len(word.group()) < 3:
		return 'sqk'
	elif len(word.group()) < 5:
		return 'SQUEAK'
	else:
		match randint(0,6):
			case 0:
				return 's'+str('q'*(len(word.group())-1))+'rk'
			case 1:
				return 'squ'+str('i'*(len(word.group())-1))+'rk'
			case 2:
				return 'squ'+str('i'*(len(word.group())-1))+'sh'
			case 3:
				return 'fw'+str('o'*(len(word.group())-1))+'mp'
			case 4:
				return 'fw'+str('w'*(len(word.group())-1))+'mp'
			case 5:
				return 'cr'+str('e'*(len(word.group())-1))+'ak'
			case 6:
				return '**Smile!**'
			case 7:
				return 'Rosa'


async def setup(bot):
	await bot.add_cog(Squeak_Cog(bot))

