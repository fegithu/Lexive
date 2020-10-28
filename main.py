from typing import Optional

import discord
import csv
from discord.ext import commands

import config

VERSION = "0.1"
AUTHOR = "Anilyka Barry"

player_cards = {}
ctypes = {"G": "Gem", "R": "Relic", "S": "Spell"}

def load():
    print("Loading content")
    player_cards.clear()
    with open("player_cards.csv", newline="") as csv_file:
        content = csv.reader(csv_file, dialect="excel", delimiter=";")
        for name, ctype, cost, code, special, text, flavour, starter, wave, box, deck, start, end in content:
            if not name or name.startswith("#"):
                continue
            special = special.replace("#", "\n")
            text = text.replace("#", "\n")
            casefolded_name = name.lower().replace(" ", "").replace("'", "").replace(",", "")
            player_cards[casefolded_name] = {
                "name": name, "type": ctype, "cost": int(cost), "code": code,
                "special": special, "text": text, "flavour": flavour, "wave": int(wave),
                "starter": starter, "box": box, "deck": deck, "start": int(start), "end": int(end)
            }

    print("Player cards loaded")

load()

class Lexive(commands.Bot):
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith(config.prefix):
            content = message.content.lstrip(config.prefix)
            values = get_player_card(content)
            if values:
                await message.channel.send("\n".join(values))
                return

        await super().on_message(message)

bot = Lexive(command_prefix=config.prefix, owner_id=config.owner)

def player_card(name: str) -> list:
    c = player_cards[name]
    values = [f"```{c['name']}", "", f"Type: {ctypes[c['type']]}", f"Cost: {c['cost']}", ""]
    if c['special']:
        values.append(f"** {c['special']} **")
        values.append("")
    values.append(f"{c['text']}")
    values.append("")
    if c['flavour']:
        values.append(f"{c['flavour']}")
        values.append("")
    if c['starter']:
        values.append(f"Starter card for {c['starter']}")
        values.append("")
    values.append(f"From {c['box']} (Wave {c['wave']})")

    if c['deck']:
        values.append(f"Deck {c['deck']}, {c['start']}-{c['end']}")
    else:
        values.append(f"{c['start']}-{c['end']}")

    values.append("```")

    return values

def get_player_card(name: str) -> Optional[list]:
    mention = None # Optional
    if "<@!" in name and ">" in name: # mentioning someone else
        index = name.index("<@!")
        name, mention = name[:index], name[index:]
    for x in ("@", "#"): # ignore what's after
        if x in name:
            name = name[:name.index(x)]
    arg = name.lower().replace(" ", "").replace("'", "").replace(",", "")
    if arg in player_cards:
        values = player_card(arg)
        if mention is not None:
            values.insert(0, mention)
        return values
    return None

@bot.command()
async def card(ctx, *args):
    values = get_player_card("".join(args))
    if values:
        to_send = "\n".join(values)
    else:
        to_send = f"No player card found matching {' '.join(args)}"

    await ctx.send(to_send)

@bot.command()
async def echo(ctx):
    await ctx.send("```When you cast a spell with Echo, resolve that Cast effect twice. "+
    "Any additional effects granted for casting the spell are added to both resolutions of the spell. "+
    "For example, you cast a spell with Echo that has a Cast effect if \"Deal 2 damage\". "+
    "That spell was prepped to a breach that has the following two effects: \"Deals +1 damage\" "+
    "and \"Gravehold gains 1 life\". You will resolve the following: \"Deal 3 damage. Gravehold gains 1 life\" "+
    "then \"Deal 3 damage. Gravehold gains 1 life\"```")

@bot.command()
async def wandering(ctx):
    await ctx.send("```Some minions have Wandering. This means that all damage dealt to them "+
    "by abilities and cards is reduced to 1. However, players may spend aether ($) to deal "+
    "these types of minions an equivalent amount of damage.```")

@bot.command()
async def reload(ctx):
    if ctx.author.is_owner():
        load()
        await ctx.send("Reloaded data.")

@bot.command()
async def whoami(ctx):
    author = AUTHOR
    owner = ctx.bot.get_user(config.owner)
    if owner is not None:
        author += f" ({owner.mention})"
    await ctx.send(f"I am Lexive v{VERSION} and I was created by {author}. "+
    "My code is available at <https://github.com/Vgr255/Lexive> where you can submit bug reports.\n" +
    "I am a utility bot for all Aeon's End content. You can ask me about any card by doing "+
    f"`{config.prefix}card <card name>` or simply `{config.prefix}<card name>` in any channel "
    "on this server. I also know about some unique mechanics.")

print("Bot loaded. Starting")

bot.run(config.token)