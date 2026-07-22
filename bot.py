"""
Bot de Discord - Proteção contra mutação do cargo 'slnK'

Este bot monitora tentativas de adicionar o cargo "Muted" (ou qualquer cargo
de mute) a membros que possuem o cargo "slnK", e reverte automaticamente
essa ação.

Requisitos:
    - Python 3.8+
    - discord.py (com intents habilitados)

Instalação:
    pip install discord.py
"""

import asyncio
import os
import discord
from discord import Member, Role, utils
from discord.ext import commands

# ─── Configuração ───────────────────────────────────────────────────────────
TOKEN = os.environ.get("DISCORD_TOKEN", "DISCORD_TOKEN")

# Nome do cargo protegido (modifique se necessário)
CARGO_PROTEGIDO_NOME = "slnK"

# Nomes de cargos que configuram mute no seu servidor (adicione os que se aplicam)
CARGOS_DE_MUTE = [
    "Muted",
    "muted",
    "Mute",
    "Silenciado",
    "Silenciado/a",
    "silenced",
    # Adicione outros nomes de cargos de mute que existam no seu servidor
]

# ─── Intents obrigatórios ──────────────────────────────────────────────────
# O bot precisa de:
#   - guilds (para acessar dados do servidor)
#   - members (para ver cargos dos membros)
#   - moderation (para detectar mudanças de cargos)
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

# ─── Bot ────────────────────────────────────────────────────────────────────
bot = commands.Bot(command_prefix="!", intents=intents)


# ─── Eventos de carregamento ───────────────────────────────────────────────
@bot.event
async def on_ready():
    """Executa quando o bot é iniciado e conectado com sucesso."""
    print(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    print(f"Protegendo o cargo: {CARGO_PROTEGIDO_NOME}")
    print(f"Monitorando cargos de mute: {CARGOS_DE_MUTE}")
    print(f"Monitorando {len(bot.guilds)} servidor(es)")


# ─── Evento principal: bloqueio de mute ────────────────────────────────────
@bot.event
async def on_member_update(before: Member, after: Member):
    """
    Detecta quando cargos de um membro são alterados.
    Se o membro possui o cargo 'slnK' e tentaram adicionar um cargo de mute,
    o bot reverte a ação imediatamente.
    """
    # Verificar se os cargos realmente mudaram
    if before.roles == after.roles:
        return

    # Verificar se o membro possui o cargo protegido (antes e depois)
    has_protected_role = any(
        role.name.lower() == CARGO_PROTEGIDO_NOME.lower()
        for role in before.roles
    )

    if not has_protected_role:
        return

    # Verificar se algum cargo de mute foi adicionado
    mute_roles_added = []
    for role in after.roles:
        if role.name in CARGOS_DE_MUTE and role not in before.roles:
            mute_roles_added.append(role)

    if not mute_roles_added:
        return

    # Remover o cargo de mute recém-adicionado
    for mute_role in mute_roles_added:
        try:
            await after.remove_roles(mute_role, reason="Proteção do cargo slnK")
            print(
                f"[PROTEÇÃO] Cargo de mute '{mute_role.name}' removido de "
                f"{after} ({after.id}) no servidor '{after.guild.name}'"
            )

            # Enviar mensagem no canal de logs (se configurado)
            log_channel = discord.utils.get(after.guild.text_channels, name="logs")
            if log_channel:
                embed = discord.Embed(
                    title="Mute Bloqueado",
                    description=(
                        f"Tentativa de mutar **{after.mention}** foi bloqueada.\n"
                        f"O membro possui o cargo protegido **{CARGO_PROTEGIDO_NOME}**."
                    ),
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow(),
                )
                embed.add_field(name="Cargo removido", value=mute_role.mention)
                embed.set_footer(text=f"ID do membro: {after.id}")
                await log_channel.send(embed=embed)

        except discord.Forbidden:
            print(
                f"[ERRO] Bot sem permissão para remover cargos de "
                f"{after} no servidor '{after.guild.name}'"
            )
        except discord.HTTPException as e:
            print(f"[ERRO HTTP] Falha ao remover cargo de {after}: {e}")


# ─── Comando de teste/status ───────────────────────────────────────────────
@bot.command(name="protecao")
async def protecao(ctx):
    """Verifica o status de proteção do bot no servidor."""
    protected_role = utils.get(ctx.guild.roles, name=CARGO_PROTEGIDO_NOME)

    if not protected_role:
        await ctx.send(f"O cargo **{CARGO_PROTEGIDO_NOME}** não foi encontrado neste servidor.")
        return

    membro_count = len(protected_role.members)
    embed = discord.Embed(
        title="Status de Proteção",
        description="Informações sobre a proteção do cargo.",
        color=discord.Color.green(),
    )
    embed.add_field(name="Cargo protegido", value=protected_role.mention)
    embed.add_field(name="Membros protegidos", value=str(membro_count))
    embed.add_field(name="Cargos de mute monitorados", value=", ".join(CARGOS_DE_MUTE))
    embed.set_footer(text="O bot está ativo e protegendo o cargo slnK.")
    await ctx.send(embed=embed)


# ─── Inicialização ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    if TOKEN == "DISCORD_TOKEN":
        print("ERRO: Defina a variável de ambiente DISCORD_TOKEN com o token do seu bot.")
        print("Ou edite este arquivo e coloque o token diretamente na variável TOKEN.")
        exit(1)

    bot.run(TOKEN)
