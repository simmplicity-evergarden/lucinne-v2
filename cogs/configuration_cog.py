from discord.ext import tasks, commands
from discord import app_commands
from discord import ui
#import re
import discord
import logging
#from random import randint
#from random import choices
#from random import randint
from typing import Literal, get_args
from typing import Union
from typing import Optional
#from typing import Optional
import guilds
from helpers import find_member

logger = logging.getLogger('bot.config')

# Simm or Owner
async def can_config(ctx):
	return (ctx.author.id == 1053028780383424563) or (ctx.guild.owner_id == context.author.id)

class Configuration_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Configuration Cog')

	@app_commands.command(description='Set roles associated with the bot')
	@commands.check(can_config)
	@app_commands.describe(affliction = "affliction/permission to assign a role to")
	@app_commands.describe(role = "role to assign to affliction")
	@app_commands.describe(clear = "use this to clear the assigned role; overrides selected role")
	async def config_roles(self,
						inter: discord.Interaction,
						affliction: Literal[guilds.affliction_list,"name_perms","speech_perms"],
						role: Optional[discord.Role],
						clear: Optional[Literal["clear role assignment"]]):

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]
		if isinstance(clear,str) and bot_guild.roles[affliction.lower()] is not None:
			del bot_guild.roles[affliction.lower()]
			logger.info(f"Removed {affliction.lower()} role setting from {inter.guild.name}")
			await inter.response.send_message(f"Removed {affliction.lower()} role setting", ephemeral=True)
		else:
			bot_guild.roles[affliction.lower()] = role.id
			logger.info(f"Set {affliction.lower()} role to {role.name} in {inter.guild.name}")
			await inter.response.send_message(f"Set {affliction.lower()} role to {role.mention}", ephemeral=True)

	@app_commands.command(description='Print config')
	@commands.check(can_config)
	async def print_config(self, inter: discord.Interaction):

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		embed = discord.Embed(title="Guild Settings")
		roles_string = ""
		for role in list(get_args(guilds.affliction_list))+["name_perms","speech_perms"]:
			if role.lower() in bot_guild.roles:
				roles_string += f"{role}: {inter.guild.get_role(bot_guild.roles[role.lower()]).mention}\n"
			else:
				roles_string += f"{role}: *unassigned*\n"

		embed.add_field(name="Roles",value=roles_string.strip(),inline=False)

		await inter.response.send_message(embed=embed, ephemeral=True)

	@app_commands.command(description='Print all user\'s statuses')
	@commands.check(can_config)
	async def print_statuses(self, inter: discord.Interaction):

		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		await inter.response.send_message("Your request is being processed. This is a potentially slow operation. Please notify Simm if you do not see a DM from the bot in the next minute or so.", ephemeral=True)

		response = "The following is a list of users and their afflictions. This list does not represent any internal order of how items are applied.\n"
		# For user in guild
		for user_id,afflictions_list in bot_guild.users.items():
			user = await find_member(self.bot, user_id, inter.guild.id)
			response += f"- {user.display_name} ({user.name})\n"
			# For affliction on user
			for affliction in afflictions_list:
				response += f"  - {type(affliction).__name__}\n"
				for key,value in affliction.__dict__.items():
					response += f"   - {key}: {value}\n"

		response += "\n**Leashes:**\n"

		for leash_mapping in bot_guild.leash_map.values():
			response += f"- {await find_member(self.bot, leash_mapping.leash_holder, inter.guild.id)}\n"
			for user_id in leash_mapping.users_leashed:
				response += f" - {await find_member(self.bot, user_id, inter.guild.id)}\n"
		await inter.user.send(response)

	@app_commands.command(description="Add/remove user in list of admins")
	async def toggle_admin(self, inter: discord.Interaction, target: discord.Member):
		bot_guild = guilds.bot_guilds[str(inter.guild_id)]

		if target.id in bot_guild.admins:
			bot_guild.admins.remove(target.id)
			await inter.response.send_message(f"{inter.author.name} removed {target.mention} from admins list.", ephemeral=True, silent=True)
			logger.info(f"Removed admin status :: {target.name}")
		else:
			bot_guild.admins.append(target.id)
			await inter.response.send_message(f"{inter.author.name} added {target.mention} to admins list.", ephemeral=True, silent=True)
			logger.info(f"Added admin status :: {target.name}")
