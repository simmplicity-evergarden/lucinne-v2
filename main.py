import bot
import logging
import logging.handlers
import os.path
from os import getenv
from dotenv import load_dotenv

def main():
	# Load env variables
	load_dotenv()

	log_location = getenv("DISCORD_BOT_LOGFILE", default=os.path.join("logs","bot.log"))

	# Ensure logs folder exists, create if it doesn't'
	if not os.path.exists(os.path.dirname(log_location)):
		os.mkdir(os.path.dirname(log_location))

	# Set log levels
	logging.getLogger('discord').setLevel(logging.INFO)
	logging.getLogger('discord.http').setLevel(logging.INFO)
	logging.getLogger('bot').setLevel(logging.DEBUG)

	# Default discord.py rotating log setup
	file_handler = logging.handlers.RotatingFileHandler(
		filename=log_location,
		encoding='utf-8',
		maxBytes=32 * 1024 * 1024,  # 32 MiB
		backupCount=5,  # Rotate through 5 files
	)

	stream_handler = logging.StreamHandler()

	dt_fmt = '%Y-%m-%d %H:%M:%S'
	formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

	file_handler.setFormatter(formatter)
	logging.getLogger('discord').addHandler(file_handler)
	logging.getLogger('bot').addHandler(file_handler)
	stream_handler.setFormatter(formatter)
	logging.getLogger('discord').addHandler(stream_handler)
	logging.getLogger('bot').addHandler(stream_handler)
	logging.getLogger('bot').info("Testing bot handler")

	bot.bot.run(getenv('DISCORD_BOT_TOKEN'), log_handler=None)

if __name__ == "__main__":
	main()
