from discord.ext import commands
from discord import app_commands
#import re
import discord
import logging
#from random import randint
from random import randint
from random import choice
from typing import Literal
from typing import Optional
import guilds
from cogs.squeak_censor_cog import censor_message
from webhooks import get_or_make_webhook
import re
import optout
# File to get the message texts from

REQUIRED_PHRASES = ["nya", "maow", "get minted"]
INTERJECTIONS = ["nya", "nyahaha", "maow"]

logger = logging.getLogger('bot.mint')

class Mint_Cog(commands.Cog):
	def Mint_Affliction(self,
		must_nyaa = False):
		return {
			"affliction_type": "mint",
			"must_nyaa": must_nyaa
			}

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Mint_Cog')


	@app_commands.command(description='Afflict mint on target')
	@app_commands.describe(target = "affliction to assign a role to")
	@app_commands.describe(must_nyaa = "must use a mint-y term like \"nyaa\" or \"get minted\" in every message")
	@app_commands.describe(clear = "use this to clear the assigned role; overrides other options")
	async def afflict_mint(self,
		inter: discord.Interaction,
		target: discord.User,
		must_nyaa: Optional[bool] = False,
		clear: Optional[Literal["clear"]] = None):

		if optout.is_optout(target.id):
			await inter.response.send_message("User has opted out of bot.", ephemeral=True)
			return 

		if inter.user.id == target.id:
			await inter.response.send_message("You cannot use this command on yourself, nyaa~")
			return

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		affliction = None
		if bot_guild["users"].get(target.id, None) is not None:
			# Filter first
			affliction = list(filter( lambda x: x["affliction_type"] == "mint", bot_guild["users"][target.id]))
			# Get first, if exists
			if len(affliction) != 0:
				affliction = affliction[0]
			else:
				affliction = None

		affliction = self.Mint_Affliction(must_nyaa)

		logger.debug(f"Affliction request: user={target.display_name}")

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

		# Ignore messages with images for sim[m]plicity's sake
		if len(message.attachments) > 0:
			return

		# Get user's affliction settings
		user_list = guilds.bot_guilds[str(message.guild.id)]["users"]
		# To get here, the user must already have the setting,
		# so we can almost guarantee it's in the list
		affliction = next(filter(
			lambda x: x["affliction_type"] == "mint",
			user_list[message.author.id]
		))

		# Pre-set these
		wm_content = None
		wm_files = []

		# If there are images in message
		for attach in message.attachments:
			wm_files.append(await attach.to_file())

		# Check for required words
		if affliction.get("must_nyaa", False):
			missing_phrase = True
			for phrase in REQUIRED_PHRASES:
				#logger.debug(f"{phrase.lower()} ::{message.content.lower()} :: {phrase.lower() in message.content.lower()} ")
				if phrase.lower() in message.content.lower():
					missing_phrase = False
			if missing_phrase:
				await message.delete()
				return
					
		# Add nyas and nyahahas
		wm_content = add_interjections(censor_message(message.content))

		if wm_content is None or wm_content.strip() == message.content.strip():
			return
		wm_content = await self.bot.get_cog("Emoji_Fix_Cog").emoji_fix(wm_content)

		await message.delete()
		webhook = await get_or_make_webhook(message.guild, message.channel)

		await webhook.send(
			wm_content,
			username=message.author.display_name,
			avatar_url=message.author.display_avatar.url,
			files=wm_files,
			silent=True,
			wait=False)

# Add interjections on whitespaces
def add_interjections(message: str) -> str:
	message = re.sub(r"[\s-]",interject_chance,message)
	return message

# ~5% chance
def interject_chance(word):
	if randint(0,100) < 5:
		return word.group() +  choice(INTERJECTIONS) + word.group()
	else:
		return word.group()
	

async def setup(bot):
	await bot.add_cog(Mint_Cog(bot))

