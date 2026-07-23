import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Servidor simples para manter o Render ativo
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot esta rodando!")

    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- CÓDIGO DO BOT ---
import asyncio
import discord
from discord import Member, Role, utils
from discord.ext import commands

TOKEN = os.environ.get("DISCORD_TOKEN", "SEU_TOKEN_AQUI")

CARGO_PROTEGIDO_NOME = "1529646696550764686"

CARGOS_DE_MUTE = [
    "Muted",
    "muted",
    "Mute",
    "Silenciado",
    "silenciado/a",
    "silenced"
]

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

@bot.event
async def on_member_update(before, after):
    cargo_protegido = utils.get(after.guild.roles, name=CARGO_PROTEGIDO_NOME)
    
    if not cargo_protegido:
        return

    tem_cargo_protegido = cargo_protegido in after.roles

    if tem_cargo_protegido:
        cargos_remover = [role for role in after.roles if role.name in CARGOS_DE_MUTE]
        
        if cargos_remover:
            try:
                await after.remove_roles(*cargos_remover, reason=f"Protecao do cargo {CARGO_PROTEGIDO_NOME}")
                print(f"Mute removido de {after.name} por ter o cargo {CARGO_PROTEGIDO_NOME}")
            except discord.Forbidden:
                print(f"Erro: Sem permissao para remover o mute de {after.name}")
            except Exception as e:
                print(f"Erro ao remover cargo: {e}")

if __name__ == "__main__":
    bot.run(TOKEN)
