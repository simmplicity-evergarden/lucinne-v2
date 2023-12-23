from discord.ext import tasks, commands
from discord import app_commands
import re
import fnmatch
import os
import discord
import logging
from random import choice
from helpers import *
from webhooks import get_or_make_webhook

censored_words_file_location = os.path.join(os.path.dirname(__file__),"..","resources","censored_words.txt")

logger = logging.getLogger('bot.censor')

censored_words = r""
if os.path.exists(censored_words_file_location):
	with open (censored_words_file_location) as censor_file:
		censored_words = r"\b("+"|".join(censor_file.read().splitlines())+r")\b"

class Squeak_Censor_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded Censor')
		# Load word list

	async def on_message(self, message):
		censored_message = censor_message(message.content)
		if censored_message == message.content:
			return
		await message.delete()
		webhook = await get_or_make_webhook(message.guild, message.channel)
		webhook_msg = await webhook.send(
			censored_message,
			username=message.author.display_name,
			avatar_url=message.author.display_avatar.url,
			silent=True)


def censor_message(message: str) -> str:
	return message
	#return re.sub(censored_words,"SQUEAK",message, flags=re.IGNORECASE)

async def setup(bot):
	await bot.add_cog(Squeak_Censor_Cog(bot))

