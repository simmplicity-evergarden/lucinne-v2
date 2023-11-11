# Example cog outlining what should be expected of a cog

from discord.ext import tasks
from discord import app_commands
import discord
import logging

# File to get something from
responses_file_location = os.path.join(os.path.dirname(__file__),"..","resources","resource.txt")
# File to save something to (persistently)
responses_file_location = os.path.join(os.path.dirname(__file__),"..","pickles","savethis.pickle")

# Logger should get bot.{shortname}
logger = logging.getLogger('bot.abc')

class Named_Cog(commands.Cog):

	# Any "Affliction" associated with the class should be here
	class Robot_Affliction():
		#
		toggle_option: bool = False


	# Things to run on bot start
	def __init__(self, bot):
		self.bot = bot

		# Message to say it was loaded
		logger.info('Loaded Robot Filter')

		# Read in any required items
		if os.path.exists(responses_file_location):
			with open(responses_file_location, 'r') as responses_file:
				for line in responses_file.readlines():
					# Add responses to dict
					response_item = line.split(',',1)
					if len(response_item) < 2:
						continue
					self.responses[response_item[0]] = response_item[1].strip()


	async def cog_load(self):
		target_guild = self.bot.get_guild(config.getint('guild','guild_id'))
		for webhook in await target_guild.webhooks():
			if webhook.name == 'rosa_bot':
				self.webhook = webhook
				# Track this separately since it seems to get lost
				config['runtime']['webhook_channel'] = str(webhook.channel_id)



	# Run message relay
	async def on_message(self, message):



	# Safeword
	async def safeword(self, bot_guild: guilds.Bot_Guild, member: discord.Member):
		# Remove the user from the
		bot_guild.users[member.id].pop
