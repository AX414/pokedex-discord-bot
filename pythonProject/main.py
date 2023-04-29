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

	# Cor azul do cartão
	embed.color = 0x3498db
	
	embed.title = "Titulo"
	embed.description = "Descricao"
	embed.add_field(name="Nome do campo", value="Texto")
	await ctx.send(embed = embed)

@bot.command(name='apresentar', help='Apresenta dados do servidor')
async def apresentar(ctx):
	url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/"
	url_thumbnail = url+"158.gif"
	url_imagem = url+"160.gif"

	nome_server = ctx.guild.name
	criador = ctx.guild.owner
	# Inclui quantia de bots
	qtd_membros = ctx.guild.member_count
	# Não inclui bots
	qtd_membros_real = len([m for m in ctx.guild.members if not m.bot]) 
	qtd_bots = qtd_membros - qtd_membros_real

	embed = discord.Embed()
	embed.color = 0x3498db
	embed.title = "Dados sobre o servidor:"
	embed.set_image(url=url_imagem)
	embed.set_thumbnail(url=url_thumbnail)
	embed.description = "Servidor: {}\nCriado por: {}\nQuantia de membros: {}\nQuantia de bots: {}\n".format(nome_server, criador, qtd_membros_real, qtd_bots)
	await ctx.send(embed=embed)

@bot.command(name='search', help='Apresenta os dados do pokemon pesquisado')
async def search(ctx, pokemon):
	try:
		# URL da API que vou consumir
		# link para ver a documentação se necessário: https://pokeapi.co/
		url = "https://pokeapi.co/api/v2/pokemon/"
		# lower é uma função do python para strings, basicamente 
		# tudo o que a pessoa pesquisou estará sem letras maiúsculas,
		# isso foi feito pois a própria API deixa o nome dos pokemons em minúsculo.
		requisicao = requests.get(url+pokemon.lower())

		pokemon = requisicao.json()

		# Apresentando o nome do pokemon por console por precausão
		print(pokemon['name'])

		# Pegando os atributos que achei pertinente
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

			elemento = ""
			if(aux == 'bug'):
				elemento = "Inseto"
				elementos+="- {}\n".format(elemento.capitalize())
			elif (aux == 'poison'):
				elemento = "Veneno"
				elementos+="- {}\n".format(elemento.capitalize())
			elif (aux == 'flying'):
				elemento = "Voador"
				elementos+="- {}\n".format(elemento.capitalize())
			elif (aux == 'dark'):
				elemento = "Sombrio"
				elementos+="- {}\n".format(elemento.capitalize())
			elif (aux == 'ground'):
				elemento = "Terra"
				elementos+="- {}\n".format(elemento.capitalize())
			else:
				elemento = GoogleTranslator(source='auto', target='pt').translate(aux)
				elementos+="- {}\n".format(elemento.capitalize())
	
			print(aux+" - "+elemento)
			i = i+1


		# Não são as cores corretas dos jogos, podem modificar para deixar igual se quiser
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
		elif p_elemento == "psychic":
			color = 0x71368a
		elif p_elemento == "fairy":
			color = 0xe91e63

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

@bot.command(name='join', help='Chama o bot para o chat de voz')
async def join(ctx):
    if not ctx.message.author.voice:
        embed = mensagem("","","","{} não está conectado à um canal de voz".format(ctx.message.author.name))
        await ctx.send(embed=embed)
        return
    else:
        voice_client = ctx.message.guild.voice_client
        if not voice_client:
            embed = mensagem("","","","Conectando ao canal de voz.")
            await ctx.send(embed=embed)
            
            channel = ctx.message.author.voice.channel
            await channel.connect()
        else:
            embed = mensagem("","","","O bot já está conectado ao canal de voz.")
            await ctx.send(embed=embed)

@bot.command(name='leave', help='Para expulsar o bot')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client:
        if voice_client.is_connected():
            embed = mensagem("","","","Desconectando do canal de voz.")
            await ctx.send(embed=embed)
            await voice_client.disconnect()
        else:
            embed = mensagem("","","","O bot não está conectado à um canal de voz.")
            await ctx.send(embed=embed)
    else:
        embed = mensagem("","","","O bot não está no canal de voz.")
        await ctx.send(embed=embed)

@bot.command(name='play', help='Toca a musica especificada pela url em seguida')
async def play(ctx,url):
    try :
        # Conecta o bot se não estiver conectado
        await join(ctx)
        # Se outra pessoa pedir para tocar, ele vai imediatamente
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        
        server = ctx.message.guild
        voice_channel = server.voice_client

        filename = await YTDLSource.from_url(url, loop=bot.loop,ctx=ctx)
            
        #windows: "C:\\ffmpeg\\bin\\ffmpeg.exe"                
        #voice_channel.play(discord.FFmpegPCMAudio(executable="caminho", source=filename))

        voice_channel.play(discord.FFmpegPCMAudio(filename, **ffmpeg_options))
    except Exception as err:
        print(err)
        return

@bot.command(name='pause', help='Pausa a música atual')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client:
        if voice_client.is_playing():
            embed = mensagem("","","","Pausando a música.")
            await ctx.send(embed=embed)
            await voice_client.pause()
        else:
            embed = mensagem("","","","O bot não está tocando no momento.")
            await ctx.send(embed=embed)
    else:
        embed = mensagem("","","","O bot não está no canal de voz.")
        await ctx.send(embed=embed)

@bot.command(name='resume', help='Continua com a música')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client:
        if voice_client.is_paused():
            embed = mensagem("","","","Continuando com a música.")
            await ctx.send(embed=embed)
            voice_client.resume()
        else:
            embed = mensagem("","","","O bot não tem nada para tocar.")
            await ctx.send(embed=embed)
    else:
        embed = mensagem("","","","O bot não está no canal de voz.")
        await ctx.send(embed=embed)


@bot.command(name='stop', help='Para a música')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client:
        if voice_client.is_playing():
            embed = mensagem("","","","Parando a música.")
            await ctx.send(embed=embed)
            await voice_client.stop()
        else:
            embed = mensagem("","","","O bot não está tocando no momento.")
            await ctx.send(embed=embed)
    else:
        embed = mensagem("","","","O bot não está no canal de voz.")
        await ctx.send(embed=embed)

@bot.command(name='help', help='Apresenta os comandos do seu bot')
async def help(ctx):
    description = '!help - Apresenta os comandos do seu bot\n'
    description+= '!mensagem - Demonstra como são as mensagens do bot\n'
    description+= '!mensagem_cartao - Demonstra como é uma embed message\n'
    description+= '!apresentar - Apresenta dados do servidor\n'
    description+= '!bot_info - Apresenta informações sobre o bot\n'
    description+= '!search <nome do pokemon ou número> - Pesquisar pokemon\n'
    description+= '\n**Comandos para Músicas:**\n'
    description+= '!join - Chama o bot para o chat de voz\n'
    description+= '!play <url> ou "pesquisa" - Toca a musica especificada pela url em seguida\n'
    description+= '!leave - Abandona o chat de voz\n'
    description+= '!pause - Pausa a música atual\n'
    description+= '!resume - Continua com a música\n'
    description+= '!stop - Para a música\n'
    
    embed = discord.Embed()
    embed.title = "Lista de Comandos:"
    embed.description = description
    embed.color = 0x3498db
    await ctx.send(embed = embed)

@bot.command(name='bot_info', help='Apresenta informações sobre o bot')
async def help(ctx):
	# Quantia de servidores que o bot está
	aux = 0
	var_nome_servers = ""
	for guild in bot.guilds:
		var_nome_servers += "-" + guild.name+"\n"
		aux += 1


	embed = discord.Embed()
	embed.color = 0x3498db
	embed.title = "Dados sobre o Bot:"
	embed.description = "Quantia de servidores que o bot está: {}".format(aux)
	embed.add_field(name="Servidores em que está:",value=var_nome_servers)
	await ctx.send(embed=embed)
	

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
