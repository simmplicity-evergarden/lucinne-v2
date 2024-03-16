from discord.ext import tasks, commands
import optout
from discord import app_commands
from discord import ui
from cogs.squeak_censor_cog import censor_message
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

logger = logging.getLogger('bot.object')

OBJECT_REGEX = re.compile('\S')

class Object_Cog(commands.Cog):
	class Object_Affliction():
		strict_mode: bool = False

		def __init__(self,
			strict_mode = False):
			self.strict_mode = strict_mode


	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Object_Cog')

	@app_commands.command(description='Afflict object on target')
	@app_commands.describe(target = "affliction to assign a role to")
	@app_commands.describe(strict_mode = "messages all become \"...\" regardless of length")
	@app_commands.describe(clear = "use this to clear the assigned role; overrides other options")
	async def afflict_object(self,
		inter: discord.Interaction,
		target: discord.User,
		strict_mode: Optional[bool] = False,
		clear: Optional[Literal["clear"]] = None):
	
		if optout.is_optout(target.id):
			await inter.response.send_message("User has opted out of bot.", ephemeral=True)
			return

		if inter.user.id == target.id:
			await inter.response.send_message("You cannot use this command on yourself, object.")
			return

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		affliction = None

		affliction = self.Object_Affliction(strict_mode)

		logger.debug(f"Affliction request: user={target.display_name} strict_mode={strict_mode} ")

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
			lambda x: type(x).__name__ == self.Object_Affliction.__name__,
			user_list[message.author.id]
		));

		# Preset this
		wm_content = None
		show_tease = False

		# Replace everything with pre-defined message
		if affliction.strict_mode:
			# Replace message
			wm_content = "....."
		# Replace non-whitespace with 
		else:
			wm_content = object_message(message.content)

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
			silent=True)


def object_message(message) -> str:
	return re.sub(OBJECT_REGEX, ".", message)

async def setup(bot):
	await bot.add_cog(Object_Cog(bot))

