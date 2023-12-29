import os
import discord
import requests
import random

from dotenv import load_dotenv
from dad_jokes import formatted_jokes
from discord.ext import commands

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
intents.messages = True

initial_activity = discord.Game(name="Write /bothelp")

bot = commands.Bot(command_prefix='/', intents=intents,
                   activity=initial_activity)


@bot.command()
async def test(ctx, arg):
    print("Command executed")
    await ctx.send(arg)


@bot.command()
async def bothelp(ctx):
    await ctx.send("Available commands: bothelp, test (arg), joke, rename (arg), update.")


@bot.command()
async def joke(ctx):
    random_index = random.randint(0, len(formatted_jokes) - 1)
    random_joke = formatted_jokes[random_index]
    await ctx.send(random_joke)


@bot.command()
async def rename(ctx, name):
    await bot.user.edit(username=name)

OPENSEA_API_URL = 'https://api.opensea.io/api/v2/listings/collection/pixels-farm/best?limit=1'
API_KEY = os.getenv("OPENSEA_API_KEY")

CRYPTOCOMPARE_API_URL = 'https://min-api.cryptocompare.com/data/price'
CRYPTOCOMPARE_API_PARAMS = {'fsym': 'ETH', 'tsyms': 'USD,PLN'}


@bot.command()
async def update(ctx):
    try:
        headers = {'Accept': 'application/json', 'X-API-KEY': API_KEY}
        response = requests.get(OPENSEA_API_URL, headers=headers)
        response.raise_for_status()

        collection_data = response.json()
        listings = collection_data.get('listings', [])

        if listings:
            first_listing = listings[0]
            price_in_wei = first_listing.get(
                'price', {}).get('current', {}).get('value')

            if price_in_wei:
                price_in_eth = float(price_in_wei) / (10 ** 18)

                eth_prices = requests.get(
                    CRYPTOCOMPARE_API_URL, params=CRYPTOCOMPARE_API_PARAMS).json()
                eth_price_usd = eth_prices.get('USD') * price_in_eth
                eth_price_pln = eth_prices.get('PLN') * price_in_eth
                eth_ilosc_harnas = float(eth_price_pln) / (3.39)

                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'💰 {eth_price_usd:.2f} USD | {eth_price_pln:.2f} PLN'))
                await ctx.send(f'Collection floor price (first listing) updated to {price_in_eth} ETH | ${eth_price_usd:.2f} USD | {eth_price_pln:.2f} PLN | Harnaś cans {eth_ilosc_harnas:.0f} ')
            else:
                await ctx.send('Unable to fetch price from the first listing.')
        else:
            await ctx.send('No listings found in the response.')
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        await ctx.send('An HTTP error occurred while fetching the collection floor price.')
    except Exception as e:
        print(f'An error occurred: {e}')
        await ctx.send('An error occurred while fetching the collection floor price.')

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN.
bot.run(DISCORD_TOKEN)
