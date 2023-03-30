import discord
import os
import asyncio
import ffmpeg
import random
import json
import requests
from deep_translator import GoogleTranslator
import yt_dlp as youtube_dl
from dotenv import load_dotenv
from discord.ext import commands,tasks

load_dotenv()

DISCORD_TOKEN = os.getenv('POKE')

print(DISCORD_TOKEN)


intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': './downloads/%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
}

ffmpeg_options = {'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

titulo_video = ''

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.7):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False,ctx):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)

        titulo_video = str(data['title'])
        imagem = str(data['thumbnail'])
        #ainda dá para adicionar mais coisas

        embed = mensagem("","",imagem,"**Título:  **"+titulo_video)
        await ctx.send(embed=embed)

        return filename

# Remove o comando de ajuda padrão, eu decidi criar o meu próprio
bot.remove_command('help')

@bot.event
async def on_ready():
    print("Bot pronto para o uso.")

@bot.command(name='mensagem', help='Demonstra como são as mensagens do bot')
async def mensagem(ctx):
	await ctx.send("Essa é uma mensagem comum")
	await ctx.send("```Essa ainda é uma mensagem comum```")

@bot.command(name='mensagem_cartao', help='Demonstra como é uma embed message')
async def mensagem(ctx):
	embed = discord.Embed()
	embed.color = 0x3498db
	embed.title = "Titulo"
	embed.description = "Descricao"
	embed.add_field(name="Nome do campo", value="Texto")
	await ctx.send(embed = embed)

@bot.command(name='apresentar', help='Apresenta dados do servidor')
async def apresentar(ctx):

	nome_server = ctx.guild.name
	criador = ctx.guild.owner

	embed = discord.Embed()
	embed.color = 0x3498db
	embed.title = "Dados sobre o servidor:"
	embed.description = "Servidor: {}\nCriado por: {}\n ".format(nome_server, criador)
	await ctx.send(embed=embed)

@bot.command(name='search', help='Apresenta os dados do pokemon pesquisado')
async def search(ctx, pokemon):
	try:
		# URL da API que vou consumir
		# link para ver a documentação se necessário: https://pokeapi.co/
		url = "https://pokeapi.co/api/v2/pokemon/"
		requisicao = requests.get(url+pokemon.lower())

		pokemon = requisicao.json()

		print(pokemon['name'])

		numero = pokemon['id']
		nome = pokemon['name']
		imagem = pokemon['sprites']['versions']['generation-v']['black-white']['animated']['front_default']
		peso = pokemon['weight']/10
		altura = pokemon['height']/10

		# Pegando a lista de elementos do pokemon pesquisado
		lista_elementos = pokemon['types']

		# Apresentando a lista de elementos
		print(lista_elementos)
		# Contando quantos elementos tem na lista
		qtd_elementos = len(lista_elementos)
		print(qtd_elementos)

		# Imprimindo  cada item da lista indo de i até a quantia
		i=0
		elementos = ""

		# Salvar o primeiro elemento para mudar de cor de acordo com o tipo
		p_elemento = ""

		while i < qtd_elementos:
			aux = pokemon['types'][i]['type']['name'] 
			p_elemento = pokemon['types'][0]['type']['name']
			elemento = GoogleTranslator(source='auto', target='pt').translate(aux)
			elementos+="- {}\n".format(elemento.capitalize())
			print(elemento)
			i = i+1

		color = 0x2ecc71
		if p_elemento == "fire":
			color = 0xe74c3c
		elif p_elemento == "grass":
			color = 0x2ecc71
		elif p_elemento == "water":
			color = 0x3498db
		elif p_elemento == "poison":
			color = 0x9b59b6
		elif p_elemento == "electric":
			color = 0xf1c40f
		elif p_elemento == "ghost":
			color = 0x99aab5
		elif p_elemento == "bug":
			color = 0x1f8b4c
		elif p_elemento == "normal":
			color = 0x1abc9c

		embed = discord.Embed()

		# Capitalize() é uma função de string utilizada para deixar a 
		# primeira letra em maiúscula
		embed.title = "Informações de {}".format(nome.capitalize())

		embed.set_thumbnail(url=imagem)
		embed.description = "**Nr. {}**\nPeso: {} Kg\nAltura: {} m".format(numero,peso,altura)
		embed.add_field(name="Elementos", value="{}".format(elementos))
		embed.color = color
		await ctx.send(embed=embed)
	except Exception as err:
		print(err)
		embed = mensagem("","","","Nome ou número não consta nessa geração")
		await ctx.send(embed = embed)
		return err

@bot.command(name='help', help='Apresenta os comandos do seu bot')
async def help(ctx):

	var = "/help - Apresenta os comandos do seu bot\n"
	var+= "/mensagem - Demonstra como são as mensagens do bot\n"
	var+= "/mensagem_cartao - Demonstra como é uma embed message\n"
	var+= "/apresentar - Apresenta dados do servidor\n"
	var+= "/search - Pesquisar pokemon\n"


	embed = discord.Embed()
	embed.title = "Lista de Comandos:"
	embed.description = var
	embed.color = 0x3498db
	await ctx.send(embed = embed)

def mensagem(title,url1,url2,description):

    default = 0
    teal = 0x1abc9c
    dark_teal = 0x11806a
    green = 0x2ecc71
    dark_green = 0x1f8b4c
    blue = 0x3498db
    dark_blue = 0x206694
    purple = 0x9b59b6
    dark_purple = 0x71368a
    magenta = 0xe91e63
    dark_magenta = 0xad1457
    gold = 0xf1c40f
    dark_gold = 0xc27c0e
    orange = 0xe67e22
    dark_orange = 0xa84300
    red = 0xe74c3c
    dark_red = 0x992d22
    lighter_grey = 0x95a5a6
    dark_grey = 0x607d8b
    light_grey = 0x979c9f
    darker_grey = 0x546e7a
    blurple = 0x7289da
    greyple = 0x99aab5

    embed = discord.Embed()
    embed.color = magenta
    embed.title = title
    embed.set_thumbnail(url=url1)
    embed.set_image(url=url2)
    embed.description = description
    return embed

if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)
