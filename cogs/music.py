import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
    
        self.is_playing = False

        # arrays para som e canal
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = ""

     #procurando no youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #selecionar a primeira URL
            m_url = self.music_queue[0][0]['source']

            #removendo o primeiro elemento que está tocando
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # loop infinito checando
    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            
            #tentanto se conectar ao canal de voz do discord caso não esteja conectado

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])
            
            print(self.music_queue)
            #removendo o primeiro elemento que está tocando (pense que a fila pode conter diversas faixas)
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
            await self.vc.disconnect()

    @commands.command(name="help",alisases=['ajuda'],help="Comando de ajuda")
    async def help(self,ctx):
        helptxt = ''
        for command in self.client.commands:
            helptxt += f'**{command}** - {command.help}\n'
        embedhelp = discord.Embed(
            colour = 1646116,#grey
            title=f'Comandos do {self.client.user.name}',
            description = helptxt+''
        )
        embedhelp.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embedhelp)


    @commands.command(name="play", help="Toca uma música do YouTube",aliases=['p','tocar'])
    async def p(self, ctx, *args):
        query = " ".join(args)
        
        try:
            voice_channel = ctx.author.voice.channel
        except:
        #se o canal estiver vazio: você precisa estar conectado em um canal para o bot saber onde ir!
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Para tocar uma música, primeiro se conecte a um canal de voz.'
            )
            await ctx.send(embed=embedvc)
            return
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                embedvc = discord.Embed(
                    colour= 12255232,#vermelho
                    description = 'Algo deu errado! Tente mudar ou configurar a playlist/vídeo ou escrever o nome dele novamente!'
                )
                await ctx.send(embed=embedvc)
            else:
                embedvc = discord.Embed(
                    colour= 32768,#verde
                    description = f"Você adicionou a música **{song['title']}** à fila! \n\n Dev Amaral"
                )
                await ctx.send(embed=embedvc)
                self.music_queue.append([song, voice_channel])
                
                if self.is_playing == False:
                    await self.play_music()

    @commands.command(name="queue", help="Mostra as atuais músicas da fila.",aliases=['q','fila'])
    async def q(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f'**{i+1} - **' + self.music_queue[i][0]['title'] + "\n"

        print(retval)
        if retval != "":
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"{retval}"
            )
            await ctx.send(embed=embedvc)
        else:
            embedvc = discord.Embed(
                colour= 1646116,
                description = 'Não existe músicas na fila no momento.'
            )
            await ctx.send(embed=embedvc)

    @commands.command(name="skip", help="Pula a atual música que está tocando.",aliases=['pular'])
    @commands.has_permissions(manage_channels=True)
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            self.vc.stop()
            #tenta tocar a próxima faixa da fila (caso exista)
            await self.play_music()
            embedvc = discord.Embed(
                colour= 1646116,#meio verde
                description = f"Você pulou a música!"
            )
            await ctx.send(embed=embedvc)

    @skip.error #erros
    async def skip_error(self,ctx,error):
        if isinstance(error, commands.MissingPermissions):
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"Você precisa da permissão **Gerenciar canais** para pular músicas."
            )
            await ctx.send(embed=embedvc)     
        else:
            raise error

def setup(client):
    client.add_cog(music(client))