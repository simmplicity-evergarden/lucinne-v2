# Manage webhook caching to avoid excessive API calls

from typing import Union
import discord
import logging

webhooks = {}

async def get_or_make_webhook(guild: discord.Guild, channel: discord.channel) -> discord.Webhook:


	# If webhook already exists in webhooks cache
	if f"{guild.id}_{channel.id}" in webhooks:
		webhook = webhooks[f"{guild.id}_{channel.id}"]
	# Cache miss
	else:
		channel_webhook_list = await channel.webhooks()
		# If there's a webhook - doesn't matter which one as long as it exists
		if any(map(lambda x: x.name == "Lucinne_Webhook", channel_webhook_list)) > 0:
		#if len(channel_webhook_list) > 0:
			webhook = list(filter(lambda x: x.name == "Lucinne_Webhook", channel_webhook_list))[0]
			webhooks[f"{guild.id}_{channel.id}"] = webhook
			logging.getLogger('bot.webhooks').info(f"Cache miss - registering {webhook.name} to {guild.id}_{channel.id}")
		# If no webhooks are found, make one
		else:
			webhook = await channel.create_webhook(name="Lucinne_Webhook")
			webhooks[f"{guild.id}_{channel.id}"] = webhook
			logging.getLogger('bot.webhooks').info(f"Cache miss - creating {webhook.name} to {guild.id}_{channel.id}")



	return webhook
