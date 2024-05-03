from discord.ext import commands
import optout
from discord import app_commands
import discord
import logging
from typing import Literal
from typing import Optional
import guilds

logger = logging.getLogger('bot.role_mgr')

class Role_Manager_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Role Manager')

	# Add/remove/toggle role
	@app_commands.command(description='Add or remove roles from a member. Defaults to toggle unless an action is specified.')
	async def manage_role(self, inter: discord.Interaction, target_member: discord.Member, perm_type: Literal["name_perms","speech_perms"], action: Optional[Literal['add','remove']]):

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]
		if optout.is_optout(target_member.id):
			await inter.response.send_message("User has opted out of bot.", ephemeral=True)
			return
		# Get role
		if perm_type.lower() in bot_guild["roles"]:
			target_role = inter.guild.get_role(bot_guild["roles"][perm_type.lower()])
		else:
			await inter.response.send_message('Permission role not defined. Please contact Simm.', ephemeral=True)
			logger.debug('Permission role not defined. Please contact Simm')
			return

		# Ready toggle action
		if action is None:
			if target_role not in target_member.roles:
				action = 'add'
			else:
				action = 'remove'

		if action == "add" and inter.user.id == target_member.id:
			await inter.response.send_message('You cannot use this command to add roles to yourself.', ephemeral=False)
			logger.debug('No self add role')
			return

		try:
			# Perform role change
			if action == 'add':
				if target_member.id == inter.user.id:
					await inter.response.send_message('You cannot restore your own permissions.', ephemeral=True)
					logger.debug(f'{inter.user.name} failed to return their own {perm_type} permissions')

				await target_member.add_roles(target_role)
				await inter.response.send_message(f'{inter.user.display_name} gave back {target_member.display_name}\'s {perm_type} permissions.', ephemeral=False)
				logger.debug(f'{inter.user.name} added {perm_type} to {target_member.display_name}')
			else:
				await target_member.remove_roles(target_role)
				await inter.response.send_message(f'{inter.user.display_name} took away {target_member.display_name}\'s {perm_type} permissions.~', ephemeral=False)
				logger.debug(f'{inter.user.name} removed {perm_type} from {target_member.display_name}')
		except Exception as err:
				await inter.response.send_message('Error occurred while running command. Please contact server admin.', ephemeral=True)
				logger.debug(f'Error occurred while {inter.user.name} did {action} action for {perm_type} perm on {target_member.name}. Error info:\n{err}')

	#async def return_perms(self, guild: discord.Guild, member: discord.Member):
	#	bot_guild = guilds.bot_guilds[str(guild.id)]


async def setup(bot):
	await bot.add_cog(Role_Manager_Cog(bot))

