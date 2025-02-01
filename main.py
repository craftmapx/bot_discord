import discord
from discord.ext import commands
import asyncio
import os
from threading import Thread  # Importado, mas não utilizado no código atual

# Configuração das intents
intents = discord.Intents.default()
intents.members = True  # Permite que o bot saiba quando membros entram ou saem
intents.message_content = True  # Permite que o bot leia o conteúdo das mensagens

# Token do bot (deve ser armazenado em uma variável de ambiente por questões de segurança)
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Inicializa o bot com um prefixo para comandos (! no caso) e as intents configuradas
bot = commands.Bot(command_prefix="!", intents=intents)

# IDs dos canais e cargos
WELCOME_CHANNEL_ID = 1333911042614628412
GENERAL_CHANNEL_ID = 1333916405149597818
ADMIN_CHANNEL_ID = 1271956942641696789
MEMBER_ROLE_ID = 1271948171135684766
ADMIN_ROLE_ID = 1271948171135684763

# Dicionário que armazena as mensagens enviadas para cada usuário
user_messages = {}

# Evento acionado quando o bot se conecta e está pronto para operar
@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')  # Imprime no console o nome do bot quando ele está pronto

# Função assíncrona que envia uma mensagem de boas-vindas com as instruções para o novo membro
async def send_welcome_message(member):
    try:
        await asyncio.sleep(5)  # Aguarda 5 segundos antes de enviar a mensagem
        channel = bot.get_channel(WELCOME_CHANNEL_ID)  # Obtém o canal de boas-vindas
        admin_role = discord.utils.get(member.guild.roles, id=ADMIN_ROLE_ID)  # Obtém o cargo de administrador

        if not channel:
            raise ValueError("Canal de boas-vindas não encontrado.")  # Erro caso o canal não seja encontrado
        if not admin_role:
            raise ValueError("Cargo de administrador não encontrado.")  # Erro caso o cargo não seja encontrado

        # Cria a mensagem de boas-vindas
        embed = discord.Embed(
            title=f"⚜ **BEM-VINDO(A), {member.name}, À FAMÍLIA 『7DS』E-SPORTS!** ⚜",
            description=(
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
            color=discord.Color.purple()  # Define a cor da borda da mensagem de boas-vindas
        )

        # Cria os botões de interação
        view = WelcomeButtons(member)
        # Envia a mensagem de boas-vindas no canal de boas-vindas
        welcome_message = await channel.send(embed=embed, view=view)
        user_messages[member.id] = welcome_message.id  # Armazena o ID da mensagem enviada

    except ValueError as e:
        # Captura e envia uma mensagem de erro se algo não for encontrado (ex.: canal ou cargo)
        print(f"Erro: {e}")
        admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
        if admin_channel:
            await admin_channel.send(f"🚨 Erro ao enviar mensagem de boas-vindas para {member.name}: {e}")
    except Exception as e:
        # Captura qualquer outro erro inesperado e notifica os administradores
        print(f"Erro inesperado: {e}")
        admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
        if admin_channel:
            await admin_channel.send(f"🚨 Erro inesperado ao tentar enviar boas-vindas para {member.name}: {e}")

# Classe que define os botões de interação com o usuário
class WelcomeButtons(discord.ui.View):
    def __init__(self, member):
        super().__init__()
        self.member = member  # Armazena o membro que interagirá com os botões

    # Botão de Aceitar, que adiciona o cargo de membro ao usuário
    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.member.id:  # Verifica se o usuário que clicou é o próprio membro
                return await interaction.response.send_message("❌ Apenas o novo membro pode interagir!", ephemeral=True)

            role = discord.utils.get(self.member.guild.roles, id=MEMBER_ROLE_ID)  # Obtém o cargo de membro
            if role:  # Se o cargo de membro for encontrado
                await self.member.add_roles(role)  # Adiciona o cargo ao membro
                await interaction.response.send_message("✅ Você agora é um membro oficial do clã 『7DS』!", ephemeral=True)
                await asyncio.sleep(5)  # Aguarda 5 segundos antes de enviar a mensagem no canal geral
                general_channel = bot.get_channel(GENERAL_CHANNEL_ID)  # Obtém o canal geral
                if general_channel:  # Se o canal geral for encontrado
                    await general_channel.send(f"🎉 Seja bem-vindo(a), {self.member.mention}, oficialmente ao clã 『7DS』E-SPORTS!")
            else:
                await interaction.response.send_message("❌ Erro ao adicionar o cargo. Contate um administrador.", ephemeral=True)

        except Exception as e:
            # Caso ocorra algum erro ao tentar adicionar o cargo ou enviar a mensagem
            print(f"Erro ao processar 'Aceitar' para {self.member.name}: {e}")
            await interaction.response.send_message("❌ Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.", ephemeral=True)

    # Botão de Recusar, que remove o usuário do servidor
    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.member.id:  # Verifica se o usuário que clicou é o próprio membro
                return await interaction.response.send_message("❌ Apenas o novo membro pode interagir!", ephemeral=True)

            # Envia uma mensagem privada informando que o usuário foi expulso por não aceitar as regras
            await self.member.send("❌ Você foi expulso do servidor por não aceitar as regras. Você pode tentar novamente quando quiser.")
            await self.member.kick(reason="Não aceitou as regras.")  # Expulsa o membro do servidor
            admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)  # Obtém o canal administrativo
            if admin_channel:  # Se o canal administrativo for encontrado
                await admin_channel.send(f"🚨 {self.member.name} foi expulso por não aceitar as regras.")  # Notifica os administradores
            await interaction.response.send_message("❌ Você foi removido do servidor.", ephemeral=True)

        except Exception as e:
            # Caso ocorra algum erro ao tentar expulsar o membro
            print(f"Erro ao processar 'Recusar' para {self.member.name}: {e}")
            await interaction.response.send_message("❌ Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.", ephemeral=True)

# Evento acionado quando um novo membro entra no servidor
@bot.event
async def on_member_join(member):
    try:
        channel = bot.get_channel(WELCOME_CHANNEL_ID)  # Obtém o canal de boas-vindas
        if not channel:
            raise ValueError("Canal de boas-vindas não encontrado.")  # Se o canal não for encontrado, levanta um erro
        await send_welcome_message(member)  # Chama a função que envia a mensagem de boas-vindas
    except ValueError as e:
        print(f"Erro: {e}")
        admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
        if admin_channel:
            await admin_channel.send(f"🚨 Erro ao processar entrada do membro {member.name}: {e}")
    except Exception as e:
        # Captura qualquer erro inesperado e notifica os administradores
        print(f"Erro inesperado ao processar entrada de {member.name}: {e}")
        admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
        if admin_channel:
            await admin_channel.send(f"🚨 Erro inesperado ao processar entrada de {member.name}: {e}")

# Inicia o bot com o token fornecido
bot.run(TOKEN)
