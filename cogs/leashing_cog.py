from discord.ext import commands
import optout
from discord import app_commands
import discord
import logging
#from random import randint
from typing import Optional
from helpers import find_member
import guilds


logger = logging.getLogger('bot.leashing')
# Permission overwrite that deny viewing a channel
no_perms = discord.PermissionOverwrite()
no_perms.view_channel = False

class Leashing_Cog(commands.Cog):
	def Leash_Mapping(self,
		leash_holder: int = 0,
		last_channel: int = 0,
		users_leashed = []):

		return {
			'leash_holder': leash_holder,
			'last_channel': last_channel,
			'users_leashed': users_leashed
			}

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded leashing Cog')


	@app_commands.command(description='Add or remove leashing (toggle).')
	@app_commands.describe(target_member = "person to be leashed")
	@app_commands.describe(holder = "person to hold the leash; defaults to you")
	async def leash(self, inter: discord.Interaction, target_member: discord.Member, holder: Optional[discord.Member]):
		# Prevent leashing the bot
		if target_member.id == self.bot.user.id:
			await inter.response.send_message('*limit-breaks so hard it crashes your game*')
			return

		if optout.is_optout(target_member.id):
			await inter.response.send_message("User has opted out of bot.", ephemeral=True)
			return

		if holder is None:
			holder = inter.user

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]
		logger.info(f'{inter.user.name} attempts to leash {target_member.name}')


		if target_member.id in bot_guild["admins"]:
			await inter.response.send_message('*limit-breaks so hard it crashes your game*')
			return


		for holder_id,leash_mapping in bot_guild["leash_map"].items():
			# Remove existing leash
			if target_member.id in leash_mapping["users_leashed"] and holder.id == leash_mapping["leash_holder"]:
				await self.remove_user_from_leash(inter.guild, holder, target_member)
				await inter.channel.send(f"Removed leash from {target_member.display_name}")
				return
			# Remove from existing leash, add the new leash
			elif target_member.id in leash_mapping["users_leashed"] and holder.id != leash_mapping["leash_holder"]:
				await self.remove_user_from_leash(inter.guild, find_member(self.bot, leash_mapping["leash_holder"], inter.guild), target_member)
				await self.add_user_to_leash(inter.guild, inter.channel, holder, target_member)
				await inter.response.send_message(f"Stole leash for {target_member.display_name}")
				return


		await self.add_user_to_leash(inter.guild, inter.channel, holder, target_member)
		await inter.channel.send(f"Leashed {target_member.display_name}")

	@app_commands.command(description='Remove all self-held leashes (may time out interaction - run twice!)')
	async def leash_removeall(self, inter: discord.Interaction):
		await self.remove_all_users_from_leash(inter.guild, inter.user)
		await inter.channel.send("Removed all leashes")

	@app_commands.command(description='Remove all leashes held by another user (may time out interaction - run twice!)')
	async def leash_removeall_admin(self, inter: discord.Interaction, holder: discord.Member):
		await self.remove_all_users_from_leash(inter.guild, holder)
		await inter.channel.send(f"Removed all leashes for {holder.display_name}")


	# Print leashed users
	async def leash_print():
		pass

	# Update leashed users
	async def on_message(self, message: discord.Message):
		await self.move_leashed_users(message.guild, message.channel, message.author, freed = False)






	# Safeword
	async def on_reaction_add(self, reaction: discord.Reaction, member: discord.Member):
		# This should only be called when safewording, so only safewording logic here
		bot_guild = guilds.bot_guilds[str(reaction.message.guild.id)]
		for leash_mapping in bot_guild["leash_map"].values():
			# Remove existing leash
			if member.id in leash_mapping["users_leashed"]:
				await self.remove_user_from_leash(reaction.message.guild, await find_member(self.bot, leash_mapping["leash_holder"], reaction.message.guild.id), member)
				logger.info(f"Removed {member.name} from leash in {reaction.message.guild.name}")
				return

	# Alias
	async def safeword(self, reaction: discord.Reaction, member: discord.Member):
		await self.on_reaction_add(reaction, member)

	async def remove_all_users_from_leash(self, guild: discord.Guild, leash_holder: discord.Member):
		# Get list of leashed members
		leash_mapping = guilds.bot_guilds[str(guild.id)]["leash_map"].get(leash_holder.id, None)
		if leash_mapping is None:
			return

		# Make copy
		leash_copy = leash_mapping["users_leashed"].copy()

		# Update all users
		for user in leash_copy:
			# Fix channel permissions for the user
			await self.fix_channel_perms(guild, guild.channels[0], await find_member(self.bot, user, guild.id), freed=True)

			# Remove user's ID from leashing list
			leash_mapping["users_leashed"].remove(user)

	async def add_user_to_leash(self, guild: discord.Guild, allowed_channel: discord.channel, leash_holder: discord.Member, target_member: discord.Member):
		# Get list of leashed members
		leash_mapping = guilds.bot_guilds[str(guild.id)]["leash_map"].get(leash_holder.id, None)
		if leash_mapping is None:
			guilds.bot_guilds[str(guild.id)]["leash_map"][leash_holder.id] = self.Leash_Mapping(
				leash_holder.id, allowed_channel.id, [])
			leash_mapping = guilds.bot_guilds[str(guild.id)]["leash_map"][leash_holder.id]

		# Fix channel permissions for the user
		await self.fix_channel_perms(guild, allowed_channel, target_member)

		# Remove user's ID from leashing list
		leash_mapping["users_leashed"].append(target_member.id)

	# Remove a user from a leash
	async def remove_user_from_leash(self, guild: discord.Guild, leash_holder: discord.Member, target_member: discord.Member):
		# Get list of leashed members
		leash_mapping = guilds.bot_guilds[str(guild.id)]["leash_map"].get(leash_holder.id, None)
		if leash_mapping is None:
			return

		# Fix channel permissions for the user
		await self.fix_channel_perms(guild, guild.channels[0], target_member, freed=True)

		# Remove user's ID from leashing list
		leash_mapping["users_leashed"].remove(target_member.id)

	# Fix channel permissions for all leashed members of a given leash holder
	async def move_leashed_users(self, guild: discord.Guild, allowed_channel: discord.channel, leash_holder: discord.Member, freed = False):
		try:
			# Get list of leashed members
			leash_mapping = guilds.bot_guilds[str(guild.id)]["leash_map"][leash_holder.id]
		except Exception as err:
			err
			return

		# Small check for empty lists
		if len(leash_mapping["users_leashed"]) == 0:
			del guilds.bot_guilds[str(guild.id)]["leash_map"][leash_holder.id]


		# Avoid updating if already in the right place
		if leash_mapping["last_channel"] == allowed_channel.id and not freed:
			return
		else:
			logger.debug(f"moving {leash_holder.display_name}'s leashed users")
			leash_mapping["last_channel"] = allowed_channel.id
			for user in leash_mapping["users_leashed"]:
				await self.fix_channel_perms(guild, allowed_channel, await find_member(self.bot, user, guild.id), freed)

	# Fix channel permissions for an individual member
	async def fix_channel_perms(self, guild: discord.Guild, allowed_channel: discord.channel, target_member: discord.Member, freed = False):
		bot_member_obj = await find_member(self.bot, self.bot.user.id, guild.id)
		for channel in guild.channels:
			# Does the bot have manage_channel perms?
			# Also skip categories
			if not channel.permissions_for(bot_member_obj).manage_channels or isinstance(channel, discord.CategoryChannel):
				continue

			print(target_member)
			print()

			# Allow only the channel that is designated as allowed, or all if freed
			if channel.id == allowed_channel.id or freed:
				await channel.set_permissions(target_member, overwrite = None)
			else:
				await channel.set_permissions(target_member, overwrite = no_perms)

async def setup(bot):
	await bot.add_cog(Leashing_Cog(bot))

