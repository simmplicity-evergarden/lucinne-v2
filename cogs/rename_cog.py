from discord.ext import commands
from discord import app_commands
import discord
import logging
import optout

logger = logging.getLogger('bot.renamer')

class Rename_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Renamer')

	# Add/remove/toggle role
	@app_commands.command(description='Change a member\'s nickname.')
	async def manage_name(self, inter: discord.Interaction, target_member: discord.Member, nickname: str):
		# Mod role check
		#mod_role = inter.guild.get_role(config.getint('roles','meanie_role'))
		#if mod_role not in inter.user.roles:
		#	await inter.response.send_message('You do not have permission to do this.', ephemeral=True)
		#	logger.info(f'User {inter.user.name} failed mod check to change roles on {target_member.name}.')
		#	return
		if optout.is_optout(target_member.id):
			await inter.response.send_message("User has opted out of bot.", ephemeral=True)
			return

		# Prevent changing own nickname
		if inter.user.id == target_member.id:
			await inter.response.send_message('You cannot change your own name using this command.', ephemeral=False)
			logger.info(f'Denied self-name-change for {target_member.name} on {inter.guild.name}')
			return

		if len(nickname) > 32:
			await inter.response.send_message('Nicknames can only be a maximum of 32 characters', ephemeral=True)
			logger.info(f'Nickname {nickname} is too long.')
			return

		old_nick = target_member.display_name

		await target_member.edit(nick=nickname)
		await inter.response.send_message(f'{inter.user.display_name} has renamed {old_nick} to {nickname}.~', ephemeral=False)
		logger.info(f'{inter.user.display_name} changed {target_member.display_name}\'s nickname to {nickname}.')
		return


async def setup(bot):
	await bot.add_cog(Rename_Cog(bot))

