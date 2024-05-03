from discord.ext import commands
import logging

logger = logging.getLogger('bot.silly')

# Simm
async def is_simm(ctx):
	return (ctx.author.id == 1053028780383424563)


class Silly_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded Silly')


	@commands.command()
	async def pawbs(self, context: commands.Context):
		await context.reply('Quick! \@simmpli.city! Look at the pawbs! ')


	@commands.command()
	async def paws(self, context: commands.Context):
		await context.reply('Did you mean \@simmpli.city?')

	@commands.command()
	async def banned(self, context: commands.Context):
		await context.send(f'banning {context.author.display_name}')

	@commands.command()
	async def mudae(self, context: commands.Context):
		await context.reply('https://www.psychologytoday.com/us/therapists')

	@commands.command()
	async def brainrot(self, context: commands.Context):
		await context.reply('Registered new brainrot to database')

	@commands.command()
	async def simmtech(self, context: commands.Context):
		await context.reply("SimmTech employs only the laziest secretaries. They're never around when needed. <@233769716198539264>")

	@commands.command()
	async def chocobo(self, context: commands.Context):
		await context.reply("oɥᴉɯ")
	
	@commands.command()
	async def e621(self, context: commands.Context):
		await context.reply("https://e621.net/posts?tags=silvia_%28silv_tsune%29+")
	
	@commands.command()
	async def tick(self, context: commands.Context):
		await context.reply("||Tick, tick, tick...\nShrink, shrink, shrink...||")


	@commands.command()
	async def ffxiv(self, context: commands.Context):
		await context.reply('Did uwu know thawt the cwiticawwy accwaimed MMOWPG finaw fantasy xiv has a fwee twiaw, awnd incwudes the entiwety of A Weawm Webown AWND the awawd-winning Stowmbwood expansion up tuwu wevew 70 with no westwictions own pwaytime? sign up, awnd enjoy Eowzea today!')

	@commands.command()
	async def lightmode(self, context: commands.Context):
		await context.reply("**Why does Simm use light mode?**\nSimm originally used light mode to separate the Simm account from an account that IRL people knew about (because who wants to explain why they are on the inflatable TF server, or why their pfp is a furry). It was easier to tell the accounts apart at a glance with different color schemes and the Nitro themes didn't exist at the time. \nNow Simm uses it out of preference and flashbangs everyone when posting screenshots of Discord's UI.")



	@commands.command()
	async def remindme(self, context: commands.Context):
		if context.author.id != 153857426813222912:
			await context.reply('What am I? Your retainer?')
		else:
			await context.reply('Oh, so *my* retainer is trying to order *me* around? Back to ventures, gilsub.')
			

	@commands.command()
	async def breach(self, context: commands.Context):
		await context.send("**Pawslut containment breach.** Deploying pawslut distraction kit:\n🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾", silent=True)

	@commands.command()
	async def emergency(self, context: commands.Context):
		await context.send(
		"Deploying Emergency Bubble Wrap\n"
		"||pop||||pop||||pop||||pop||||pop||||pop||||pop||\n"
		"||pop||||pop||||pop||||pop||||pop||||pop||||pop||\n"
		"||pop||||pop||||pop||||pop||||pop||||pop||||pop||\n"
		"||pop||||pop||||pop||||pop||||pop||||pop||||pop||\n"
		"||pop||||pop||||pop||||pop||||pop||||pop||||pop||\n"
		"||pop||||pop||||pop||||pop||||pop||||pop||||pop||\n"
		"||pop||||pop||||pop||||pop||||pop||||pop||||pop||"
		, silent=True)

	@commands.command()
	async def emergencypaws(self, context: commands.Context):
		await context.send(
		"Deploying Emergency Bubble Wrap\n"
		"||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||\n"
		"||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||\n"
		"||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||\n"
		"||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||\n"
		"||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||\n"
		"||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||\n"
		"||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||||:feet:||"
		, silent=True)



	@commands.command()
	@commands.check(is_simm)
	async def selfdestruct(self, context: commands.Context):
		await context.send('i\'m deleting this server and then myself. sayonara you weeaboo shits.')
		exit()




async def setup(bot):
	await bot.add_cog(Silly_Cog(bot))

