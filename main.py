import discord
from discord.ext import commands, tasks
import asyncio
import os
import datetime

# Configuração de Intents para permitir que o bot acesse eventos de membros e mensagens
intents = discord.Intents.default()
intents.members = True  # Necessário para detectar novos membros
intents.message_content = True  # Permite acessar o conteúdo das mensagens

# Token do bot (deve ser definido como variável de ambiente por segurança)
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Inicializa o bot com prefixo "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# IDs dos canais e cargo
WELCOME_CHANNEL_ID = 1333911042614628412  # Canal de boas-vindas
GENERAL_CHANNEL_ID = 1333916405149597818  # Canal geral
ADMIN_CHANNEL_ID = 1271956942641696789  # Canal de administradores
MEMBER_ROLE_ID = 1271948171135684766  # Cargo de membro
ADMIN_ROLE_ID = 1271948171135684763  # Cargo de administrador

# Dicionário para armazenar mensagens enviadas para cada usuário
user_messages = {}
joined_members = []  # Lista para armazenar os membros que entraram durante a noite

@bot.event
async def on_ready():
    """Evento acionado quando o bot está pronto para uso."""
    print(f'✅ Bot conectado como {bot.user}')
    check_time_and_toggle.start()  # Inicia a checagem do horário
    await check_members_who_joined_while_off()  # Verifica os membros que entraram enquanto o bot estava desligado

async def send_welcome_message(member, apology_text=""):
    """Envia uma mensagem de boas-vindas ao novo membro após um pequeno atraso."""
    await asyncio.sleep(5)  # Aguarda 5 segundos antes de enviar a mensagem
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    admin_role = discord.utils.get(member.guild.roles, id=ADMIN_ROLE_ID)

    if channel and admin_role:
        # Criando um embed de boas-vindas para o novo membro
        embed = discord.Embed(
            title=f"⚜ **BEM-VINDO(A), {member.name}, À 『7DS』E-SPORTS!** ⚜",
            description=(
                f"{apology_text}\n\n"
                "Estamos muito felizes em tê-lo(a) conosco!\n\n"
                "Nosso clã 『7DS』E-SPORTS é um grupo de jogadores focados no competitivo e na amizade verdadeira. "
                "Buscamos jogadores ativos que compartilhem do nosso objetivo: **dominar as partidas enquanto nos divertimos** "
                "e criamos laços sólidos. Se você gosta de desafios, ranqueadas e quer crescer junto com uma equipe organizada, "
                "**você está no lugar certo!**\n\n"
                "📜 **REGRAS DO CLÃ E DA COMUNIDADE** 📜\n"
                "✅ **Respeito acima de tudo**: Trate todos os membros com respeito.\n"
                "🚫 **Proibido conteúdo inapropriado**: Não compartilhe mensagens ofensivas.\n"
                "📵 **Sem spam**: Não envie links irrelevantes.\n"
                "🔒 **Privacidade e segurança**: Não compartilhe dados pessoais sem consentimento.\n"
                "🏷 **Tag obrigatória**: Adicione 『7DS』 ao seu nickname.\n"
                "🎮 **Fechar Squad com membros**: Priorize jogar com outros membros do clã.\n"
                "⏳ **Participação ativa**: Se ficar offline por **15 dias**, poderá ser removido.\n"
                "❌ **Proibido comportamento tóxico**: Discussões e brigas não serão toleradas.\n\n"
                "⚔ **Para entrar no clã, siga os passos abaixo:**\n"
                "1️⃣ Leia e aceite todas as regras no canal <#1271948171601510555>.\n"
                "2️⃣ Adicione a tag oficial 『7DS』 no seu nome.\n"
                "3️⃣ Clique no botão **'Aceitar'** abaixo para entrar, ou **'Recusar'** para sair.\n\n"
                "❓ Se tiver dúvidas, pergunte no canal <#1272070605088493642>.\n"
                "🎮 Boa sorte e divirta-se! 🏆"
            ),
            color=discord.Color.purple()
        )
        
        view = WelcomeButtons(member)  # Adiciona os botões interativos
        welcome_message = await channel.send(embed=embed, view=view)
        
        # Armazena a ID da mensagem de boas-vindas para referência futura
        user_messages[member.id] = welcome_message.id

class WelcomeButtons(discord.ui.View):
    """Cria botões interativos para aceitar ou recusar a entrada no clã."""
    def __init__(self, member):
        super().__init__()
        self.member = member

    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botão para aceitar e adicionar o cargo de membro."""
        if interaction.user.id != self.member.id:
            return await interaction.response.send_message("❌ Apenas o novo membro pode interagir!", ephemeral=True)

        role = discord.utils.get(self.member.guild.roles, id=MEMBER_ROLE_ID)
        if role:
            await self.member.add_roles(role)
            await interaction.response.send_message("✅ Você agora é um membro oficial da familia『7DS』!", ephemeral=True)

            await asyncio.sleep(5)  # Aguarda antes de anunciar a entrada no chat geral
            general_channel = bot.get_channel(GENERAL_CHANNEL_ID)
            if general_channel:
                await general_channel.send(f"🎉 Seja bem-vindo(a), {self.member.mention}, oficialmente ao clã 『7DS』E-SPORTS!")
        else:
            await interaction.response.send_message("❌ Erro ao adicionar o cargo. Contate um administrador.", ephemeral=True)

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botão para recusar e expulsar o membro do servidor."""
        if interaction.user.id != self.member.id:
            return await interaction.response.send_message("❌ Apenas o novo membro pode interagir!", ephemeral=True)

        await self.member.send("❌ Você foi expulso do servidor por não aceitar as regras. Você pode tentar novamente quando quiser.")
        await self.member.kick(reason="Não aceitou as regras.")

        admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
        if admin_channel:
            await admin_channel.send(f"🚨 {self.member.name} foi expulso por não aceitar as regras.")

        await interaction.response.send_message("❌ Você foi removido do servidor.", ephemeral=True)

@bot.event
async def on_member_join(member):
    """Evento acionado quando um novo membro entra no servidor."""
    # Verifica se o bot estava desligado e se a entrada foi à noite
    current_hour = datetime.datetime.now().hour
    if 0 <= current_hour < 8:
        joined_members.append(member)
    else:
        await send_welcome_message(member)  # Envia a mensagem de boas-vindas normal

async def check_members_who_joined_while_off():
    """Verifica os membros que entraram enquanto o bot estava desligado e envia uma mensagem personalizada."""
    for member in joined_members:
        apology_text = "Desculpe, estava dormindo! Mas agora estou aqui para te dar as boas-vindas!"
        await send_welcome_message(member, apology_text)

@tasks.loop(minutes=1)
async def check_time_and_toggle():
    """Verifica a hora e liga/desliga o bot conforme necessário."""
    current_hour = datetime.datetime.now().hour
    if 0 <= current_hour < 8:  # Bot desliga entre 00:00 e 08:00
        if bot.is_ready():
            print("Desligando o bot...")  
            await bot.close()
    elif 8 <= current_hour < 24:  # Bot liga entre 08:00 e 00:00
        if not bot.is_ready():
            print("Ligando o bot...") 
            await bot.start(TOKEN)

# Inicia o bot com o token fornecido
bot.run(TOKEN)
