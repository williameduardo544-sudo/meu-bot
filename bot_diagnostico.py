import os
import logging
import discord
from discord.ext import commands
from discord import Member

# Configuração de Log para mostrar TUDO
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("DEBUG_BOT")

TOKEN = os.environ.get("DISCORD_TOKEN")
CARGO_PROTEGIDO_ID = 1529646696550764686

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"--- BOT ONLINE: {bot.user} ---")
    print(f"Monitorando Cargo bseven ID: {CARGO_PROTEGIDO_ID}")

@bot.event
async def on_member_update(before: Member, after: Member):
    # Log de evento recebido
    print(f"\n[EVENTO] Mudança detectada no usuário: {after.name}")

    if after.bot:
        print(f" > Ignorado: É um bot.")
        return

    # 1. Verificar se o usuário tem o cargo bseven
    possui_bseven = any(role.id == CARGO_PROTEGIDO_ID for role in after.roles)
    print(f" > Tem o cargo bseven? {'SIM' if possui_bseven else 'NÃO'}")
    
    if not possui_bseven:
        return

    # 2. Listar cargos novos
    cargos_antes = set(before.roles)
    cargos_depois = set(after.roles)
    novos_cargos = cargos_depois - cargos_antes

    if not novos_cargos:
        print(" > Nenhun cargo novo foi adicionado (talvez apenas removido).")
        return

    print(f" > Cargos adicionados: {[r.name for r in novos_cargos]}")

    # 3. Verificar se algum novo cargo é de mute
    for cargo in novos_cargos:
        nome_cargo = cargo.name.lower()
        print(f" > Analisando cargo: '{nome_cargo}'")
        
        # Aumentamos a sensibilidade: qualquer coisa com 'mut' ou 'silenc'
        if "mut" in nome_cargo or "silenc" in nome_cargo:
            print(f" !!! DETECTADO CARGO DE MUTE: {cargo.name}")
            
            try:
                print(f" > Tentando remover '{cargo.name}' de {after.name}...")
                await after.remove_roles(cargo, reason="Proteção bseven")
                print(f" ✅ SUCESSO: Cargo removido!")
            except discord.Forbidden:
                print(f" ❌ ERRO DE PERMISSÃO (Forbidden):")
                print(f"    - O bot tem a permissão 'Gerenciar Cargos'?")
                print(f"    - O cargo do bot está ACIMA do cargo '{cargo.name}' na lista?")
                print(f"    - Cargo do Bot: {after.guild.me.top_role.name} (Posição: {after.guild.me.top_role.position})")
                print(f"    - Cargo de Mute: {cargo.name} (Posição: {cargo.position})")
            except Exception as e:
                print(f" ❌ ERRO INESPERADO: {e}")

if __name__ == "__main__":
    if not TOKEN:
        print("ERRO: Falta o DISCORD_TOKEN nas variáveis de ambiente.")
    else:
        bot.run(TOKEN)
