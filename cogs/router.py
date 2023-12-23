from discord.ext import commands
import discord
import logging
from guilds import bot_guilds
import guilds

# The purpose of this cog is to prevent race conditions and code reuse for commonly
# used events, namely on_message, on_reaction_add, and on_reaction_remove. Logic is
# centrally managed here and sent to the appropriate cog.

logger = logging.getLogger('bot.router')

class SpeechRouter_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Speech Router')

	#
	@commands.Cog.listener()
	async def on_message(self, message):
		# Prevent operating on bot messages
		if message.author.bot:
			return;
		# Prevent operating on webhook messages
		elif message.webhook_id is not None:
			return;
		# Guild owner mentioned
		elif message.guild.owner.id in [user.id for user in message.mentions]:
			logger.debug(f"{message.author.name} mentioned server owner")
			await self.bot.get_cog("Thrall_Cog").on_owner_mention(message)
		else:
			# Get user list
			try:
				user_list = bot_guilds[str(message.guild.id)].users
			# Hotfix for Rosa's server
			except KeyError:
				guilds.add_guild(message.guild)

			# Check that user actually exists
			if message.author.id in user_list:
				# Turn classes into class names
				list_of_afflictions = list(map(
					lambda x: type(x).__name__,
					user_list[message.author.id]
				));
			else:
				list_of_afflictions = []

			# Detect affliction
			if "Thrall_Affliction" in list_of_afflictions:
				logger.debug(f"THRALL:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Thrall_Cog").on_message(message)
			elif "Object_Affliction" in list_of_afflictions:
				logger.debug(f"OBJECT:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Object_Cog").on_message(message)
			elif "Feral_Affliction" in list_of_afflictions:
				logger.debug(f"FERAL:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Feral_Cog").on_message(message)
			elif "Squeak_Affliction" in list_of_afflictions:
				logger.debug(f"SQEAK:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Squeak_Cog").on_message(message)
			elif "Robot_Affliction" in list_of_afflictions:
				# Get specific handler to pass to
				logger.debug(f"ROBOT:{message.author.name}\t{message.content}")
				await self.bot.get_cog("Robot_Cog").on_message(message)
			else:
				await self.bot.get_cog("Squeak_Censor_Cog").on_message(message)
		
		# Separate processing for leashed users
		await self.bot.get_cog("Leashing_Cog").on_message(message)


	#
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, member):
		# ignore bot reactions
		if member.id == self.bot.user.id:
			return

		# Remove all afflictions
		if not isinstance(reaction.emoji, str) and reaction.emoji.name == 'safeword':
			# Get user list
			user_list = bot_guilds[str(reaction.message.guild.id)].users
			# Check that user actually exists
			if member.id in user_list:
				await bot_guilds[str(reaction.message.guild.id)].clear_target(self.bot, member)
				logger.debug(f'{member.name} safeworded')

			# Leashing does a lot so we'll let it handle things itself
			await self.bot.get_cog("Leashing_Cog").on_reaction_add(reaction, member)

			guild_roles = guilds.bot_guilds[str(reaction.message.guild.id)].roles

			for perm_type in ["name_perms","speech_perms"]:
				# Get role
				if perm_type.lower() in guild_roles:
					target_role = reaction.message.guild.get_role(guild_roles[perm_type.lower()])
				else:
					continue

				logger.info(f'Attempting to restore {perm_type} to {member.name} on {member.guild.name}.')

				await member.add_roles(target_role)
		
		# Squeak emoji
		elif not isinstance(reaction.emoji, str) and reaction.emoji.name == 'Rosasmile':
			await self.bot.get_cog("Squeak_Cog").on_reaction_add(reaction, member)	
		elif reaction.emoji in ['🔓','🔒','🐾','🔑']:
			await self.bot.get_cog("Feral_Cog").on_reaction_add(reaction, member)
		elif reaction.emoji in ['🎈','💬']:
			await self.bot.get_cog("Squeak_Cog").on_reaction_add(reaction, member)	

	@commands.Cog.listener()
	async def on_reaction_remove(self, reaction, member):
		# ignore bot reactions
		if member.id == self.bot.user.id:
			return

		if reaction.emoji in ['🔓','🔒','🐾','🔑']:
			await self.bot.get_cog("Feral_Cog").on_reaction_remove(reaction, member)


async def setup(bot):
	await bot.add_cog(SpeechRouter_Cog(bot))

