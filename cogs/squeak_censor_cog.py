from discord.ext import commands
import re
import os
import logging
#from helpers import *
from webhooks import get_or_make_webhook
from unidecode import unidecode

censored_words_file_location = os.path.join(os.path.dirname(__file__),"..","resources","censored_words.txt")

logger = logging.getLogger('bot.censor')

ignored_chars = r"[^A-Za-z0-9]"
censored_words = r""
if os.path.exists(censored_words_file_location):
	with open (censored_words_file_location) as censor_file:
		censored_words = r"("+"|".join(censor_file.read().splitlines())+r")"

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
		await webhook.send(
			censored_message,
			username=message.author.display_name,
			avatar_url=message.author.display_avatar.url,
			silent=True)


def censor_message(message: str) -> str:
	return message
	temp_message = re.sub(ignored_chars,"",unidecode(message), flags=re.IGNORECASE)
	matches = re.findall(censored_words, temp_message, flags=re.IGNORECASE)
	new_phrase = unidecode(message)
	for i in matches:
		new_phrase = re.sub("("+"[^A-Za-z0-9]*".join(list(i))+")", wordrepl, new_phrase, flags=re.IGNORECASE)
		
	print(new_phrase)

	return new_phrase
	return message
	#return re.sub(censored_words,"SQUEAK",message, flags=re.IGNORECASE)

def wordrepl(matchobj):
	word = matchobj.group(0)
	for i in range(len(word)):
		if word[i].isalnum():
			word = word[:i] + "?" + word[i+1:]
	return word

async def setup(bot):
	await bot.add_cog(Squeak_Censor_Cog(bot))

