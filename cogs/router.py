from discord.ext import commands
import logging
from guilds import bot_guilds
import guilds
import optout

# The purpose of this cog is to prevent race conditions and code reuse for commonly
# used events, namely on_message, on_reaction_add, and on_reaction_remove. Logic is
# centrally managed here and sent to the appropriate cog.

logger = logging.getLogger('bot.router')

class SpeechRouter_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Speech Router')

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		# Pass off to normal parser
		await self.on_message(after)

	#
	@commands.Cog.listener()
	async def on_message(self, message):
		# Prevent operating on bot messages
		if message.author.bot:
			return
		if message.guild is None:
			await optout.optout(message)
			return
		if optout.is_optout(message.author.id):
			return
		# Prevent operating on webhook messages
		elif message.webhook_id is not None:
			return
		else:
			# Guild owner mentioned
			if message.guild.owner.id in [user.id for user in message.mentions]:
				logger.debug(f"{message.author.name} mentioned server owner")
				await self.bot.get_cog("Thrall_Cog").on_owner_mention(message)
			
			# Get user list
			try:
				user_list = bot_guilds[str(message.guild.id)]["users"]
			# Hotfix for Rosa's server
			except KeyError:
				guilds.add_guild(message.guild.id)
				user_list = bot_guilds[str(message.guild.id)]["users"]

			# Check that user actually exists
			if message.author.id in user_list:
				# Turn classes into class names
				list_of_afflictions = list(map(
					lambda x: x["affliction_type"],
					user_list[message.author.id]
				))
			else:
				list_of_afflictions = []

			# Detect affliction
			if "thrall" in list_of_afflictions:
				logger.debug(f"THRALL:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Thrall_Cog").on_message(message)
			elif "object" in list_of_afflictions:
				logger.debug(f"OBJECT:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Object_Cog").on_message(message)
			elif "mint" in list_of_afflictions:
				logger.debug(f"MINTED:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Mint_Cog").on_message(message)
			elif "feral" in list_of_afflictions:
				logger.debug(f"FERAL:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Feral_Cog").on_message(message)
			elif "squeak" in list_of_afflictions:
				logger.debug(f"SQEAK:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Squeak_Cog").on_message(message)
			elif "robot" in list_of_afflictions:
				# Get specific handler to pass to
				logger.debug(f"ROBOT:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Robot_Cog").on_message(message)
			else:
				# Od exception
				if message.author.id != 201821870255898625:
					await self.bot.get_cog("Squeak_Censor_Cog").on_message(message)
		
		# Separate processing for leashed users
		await self.bot.get_cog("Leashing_Cog").on_message(message)


	#
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, member):
		# ignore bot reactions
		if member.id == self.bot.user.id:
			return
		
		if member.id in [233769716198539264, 1053028780383424563]:
			if reaction.emoji != "🐾": 
				await reaction.message.remove_reaction(reaction.emoji, member)
				return
			else:
				return


		# Remove all afflictions
		if not isinstance(reaction.emoji, str) and reaction.emoji.name == 'safeword':
			# Get user list
			#user_list = bot_guilds[str(reaction.message.guild.id)]["users"]
			# Check that user actually exists
			#if member.id in user_list:
			await guilds.clear_target(str(reaction.message.guild.id), self.bot, member)
			logger.debug(f'{member.name} safeworded')

			# Leashing does a lot so we'll let it handle things itself
			await self.bot.get_cog("Leashing_Cog").on_reaction_add(reaction, member)

			guild_roles = guilds.bot_guilds[str(reaction.message.guild.id)]["roles"]

			for perm_type in ["name_perms","speech_perms"]:
				# Get role
				if perm_type.lower() in guild_roles:
					target_role = reaction.message.guild.get_role(guild_roles[perm_type.lower()])
				else:
					continue

				if member.id == 167374359944495104 and "name" in perm_type:
					continue

				logger.info(f'Attempting to restore {perm_type} to {member.name} on {member.guild.name}.')

				await member.add_roles(target_role)

			if optout.is_optout(member.id):
				return

	
		# Squeak emoji
		elif not isinstance(reaction.emoji, str) and reaction.emoji.name == 'Rosasmile':
			await self.bot.get_cog("Squeak_Cog").on_reaction_add(reaction, member)	
		elif reaction.emoji in ['🔋','🗝️']:
			await self.bot.get_cog("Robot_Cog").on_reaction_add(reaction, member)
		elif reaction.emoji in ['🔓','🔒','🐾','🔑']:
			await self.bot.get_cog("Feral_Cog").on_reaction_add(reaction, member)
		elif reaction.emoji in ['🎈','💬']:
			await self.bot.get_cog("Squeak_Cog").on_reaction_add(reaction, member)	

	@commands.Cog.listener()
	async def on_reaction_remove(self, reaction, member):
		# ignore bot reactions
		if member.id == self.bot.user.id:
			return

		if optout.is_optout(member.id):
			return

		if reaction.emoji in ['🔓','🔒','🐾','🔑']:
			await self.bot.get_cog("Feral_Cog").on_reaction_remove(reaction, member)


async def setup(bot):
	await bot.add_cog(SpeechRouter_Cog(bot))
