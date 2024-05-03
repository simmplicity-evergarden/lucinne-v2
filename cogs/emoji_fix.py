from discord.ext import commands
import discord
import logging
import re
import requests
from PIL import Image
from io import BytesIO

logger = logging.getLogger('bot.fix')
REFERENCE_SERVER = 1112852298721407006

EMOJI_REGEX = re.compile("<(a?):[A-Za-z0-9_\-]+:([0-9]+)>")

# Simm
async def is_simm(ctx):
	return (ctx.author.id == 1053028780383424563)


class Emoji_Fix_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded Emoji Fix')


	@commands.command()
	async def emoji(self, context: commands.Context):
		await context.channel.send(await self.emoji_fix(context.message.content))


	# Function to pass all messages through to fix emojis
	async def emoji_fix(self, message: str) -> str:
		new_message = message
		# Get matches for emoji sequence
		matches = re.finditer(EMOJI_REGEX, message)
		for i in matches:
			# Check for replace requirement
			animated = i[1] == "a"
			identifier = i[2]
			emoji_result = await self.check_for_emoji(identifier)
			# Local emoji, no change needed
			if emoji_result == 0:
				continue
			# Remote emoji, upload needed
			elif emoji_result < 1:
				emoji_result = await self.upload_emoji(animated, identifier)
			
			#print(i[0])
			#print(new_message)
			#print(i[0] in new_message)
			new_message = new_message.replace(i[0],f"<{i[1]}:{i[2]}:{emoji_result}>")
			#print(new_message)
		#print(new_message)
		return new_message


	# >0 : in reference server
	# 0  : local to server
	# <0 : needs to be uploaded
	async def check_for_emoji(self, identifier: str) -> int:
		# Needed for emote check + upload
		guild = self.bot.get_guild(REFERENCE_SERVER)
		
		# Test for generally available emoji
		if self.bot.get_emoji(int(identifier)) is not None:
			#print("Emoji already available - local")
			return 0

		# Test ref serv
		emoji = discord.utils.get(guild.emojis, name=identifier)
		if emoji is not None:
			#print("Emoji already available - ref serv")
			return emoji.id
		else:
			return -1

	

	# return new emoji's ID
	async def upload_emoji(self, animated: bool, identifier: str):

		logger.info(f"Adding new emote to ref server: {identifier}")

		if not animated:
			target = f"https://cdn.discordapp.com/emojis/{identifier}.webp"
		else: 
			target = f"https://cdn.discordapp.com/emojis/{identifier}.gif"
		#print(target)

		# Download target
		r = requests.get(target)
		#print(type(r.content))
		
		# If webp, must convert
		if not animated:
			bio_object = BytesIO()
			# Open in memory
			converted_image = Image.open(BytesIO(r.content))
			# Save to bytes IO 
			converted_image.save(bio_object, format="png")
			# Reset position and read
			bio_object.seek(0)
			uploadable_image = bio_object.read()
			#print(uploadable_image)
		else:
			uploadable_image = r.content

		guild = self.bot.get_guild(REFERENCE_SERVER)
		# Verify space for upload
		if len(guild.emojis) > 45:
			await guild.delete_emoji(guild.emojis[0]) 

		new_emoji = await guild.create_custom_emoji(
			name=identifier,
			image=uploadable_image
			)
		return new_emoji.id


async def setup(bot):
	await bot.add_cog(Emoji_Fix_Cog(bot))

