import discord
from guilds import optouts
from typing import Union

async def optout(message: discord.Message):
	if "optout" in message.content.lower():
		if is_optout(message.author.id):
			await message.reply("You have already been opted out of all bot interactions.")
		else:
			optouts[str(message.author.id)] = "optout"
			await message.reply("You have been opted out of all bot interactions.")
	

def is_optout(user: Union[int, str]):
	if isinstance(user,int):
		user = str(user)
	return user in optouts
