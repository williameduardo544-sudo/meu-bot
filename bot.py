import os
import logging
import threading
import discord
from flask import Flask
from discord.ext import commands
from discord import Member

# ─── CONFIGURAÇÕES DE LOGGING ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ModerationBot")

# ─── CONFIGURAÇÕES DO BOT ──────────────────────────────────────────────────
TOKEN = os.environ.get("DISCORD_TOKEN")
CARGO_PROTEGIDO_ID = 1529646696550764686  # ID do cargo 'bseven'
CARGO_BOT_ID = 1529601980505264141        # ID do cargo do Bot

# ─── INTENTS ───────────────────────────────────────────────────────────────
# Necessário habilitar 'Server Members Intent' no Discord Developer Portal
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ─── SERVIDOR WEB (KEEP-ALIVE PARA RENDER/CLOUD) ──────────────────────────
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Proteção bseven está ONLINE!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ─── EVENTOS ───────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    logger.info(f"Bot logado como {bot.user} (ID: {bot.user.id})")
    logger.info(f"Protegendo cargo ID: {CARGO_PROTEGIDO_ID}")

@bot.event
async def on_member_update(before: Member, after: Member):
    """
    Lógica de Proteção: Monitora mudanças de cargos.
    Se um membro com o cargo 'bseven' receber um cargo de 'mute', o bot remove.
    """
    
    # 1. Segurança: Ignora o próprio bot e evita loops
    if after.bot:
        return

    # 2. Verifica se houve mudança nos cargos
    if before.roles == after.roles:
        return

    # 3. Verifica se o membro possui o cargo protegido 'bseven'
    possui_bseven = any(role.id == CARGO_PROTEGIDO_ID for role in after.roles)
    if not possui_bseven:
        return

    # 4. Identifica se algum cargo novo com 'mute' no nome foi adicionado
    cargos_adicionados = [role for role in after.roles if role not in before.roles]
    
    for cargo in cargos_adicionados:
        if "mute" in cargo.name.lower():
            logger.info(f"Tentativa de mute detectada em {after.name} (Cargo: {cargo.name})")
            
            try:
                # Remove o cargo de mute
                await after.remove_roles(cargo, reason="Proteção Automática: Membro possui cargo bseven.")
                logger.info(f"Sucesso: Cargo '{cargo.name}' removido de {after.name}.")
                
            except discord.Forbidden:
                logger.error(
                    f"ERRO DE PERMISSÃO: Não foi possível remover o cargo de {after.name}. "
                    "Verifique se o cargo do bot está ACIMA do cargo de mute na hierarquia "
                    "e se a permissão 'Gerenciar Cargos' está ativa."
                )
            except Exception as e:
                logger.error(f"ERRO INESPERADO ao processar {after.name}: {e}")

# ─── INICIALIZAÇÃO ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not TOKEN:
        logger.critical("ERRO: Variável de ambiente DISCORD_TOKEN não encontrada!")
    else:
        # Inicia o servidor web em uma thread separada
        threading.Thread(target=run_web_server, daemon=True).start()
        # Inicia o bot do Discord
        bot.run(TOKEN)
