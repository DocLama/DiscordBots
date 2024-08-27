import discord
from discord.ext import commands
import json
import os

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)  # Utilisation du préfixe '!' pour les commandes

# Fichier JSON pour stocker les combinaisons
data_file = 'combinations.json'

# Fonction pour charger les combinaisons depuis le fichier JSON
def load_combinations():
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Le fichier JSON est vide ou corrompu, création d'un tableau vide.")
            return []
    return []

# Fonction pour sauvegarder les combinaisons dans le fichier JSON
def save_combinations():
    with open(data_file, 'w') as f:
        json.dump(combinations, f, indent=4)

# Charger les combinaisons existantes
combinations = load_combinations()

# Commande pour ajouter une combinaison
@bot.command(name='cadd')
async def add_combination(ctx, prop1: str, *, prop2: str):
    print("Commande cadd reçue")
    new_id = len(combinations) + 1
    combinations.append({'id': new_id, 'trigger': prop1, 'response': prop2})
    save_combinations()
    await ctx.send(f'Combinaison ajoutée ! ID: {new_id} | Si "{prop1}" est écrit, alors "{prop2}" sera envoyé.')

# Commande pour lister toutes les combinaisons
@bot.command(name='clist')
async def list_combinations(ctx):
    print("Commande clist reçue")
    
    # Définir le nombre de combinaisons par page
    items_per_page = 10
    total_pages = (len(combinations) + items_per_page - 1) // items_per_page
    
    def create_embed(page):
        embed = discord.Embed(
            title="**CasseNoix**",
            description=f"Page {page+1}/{total_pages}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url="attachment://logo.jpg")
        
        start = page * items_per_page
        end = start + items_per_page
        for combo in combinations[start:end]:
            embed.add_field(
                name=f'ID: {combo["id"]} - Trigger : {combo["trigger"]}',
                value=f'Réponse : {combo["response"]}',
                inline=False
            )
        return embed

    current_page = 0
    file = discord.File("logo.jpg", filename="logo.jpg")
    message = await ctx.send(file=file, embed=create_embed(current_page))

    # Ajoute les réactions pour la navigation
    if total_pages > 1:
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

    # Fonction pour gérer les réactions
    def check(reaction, user):
        return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ["◀️", "▶️"]

    # Boucle pour gérer les changements de pages
    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "▶️" and current_page < total_pages - 1:
                current_page += 1
                await message.edit(embed=create_embed(current_page))
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=create_embed(current_page))
                await message.remove_reaction(reaction, user)

        except discord.errors.TimeoutError:
            break

# Commande pour supprimer une combinaison par ID
@bot.command(name='cdel')
async def delete_combination(ctx, combo_id: int):
    print("Commande cdel reçue")
    global combinations
    combinations = [combo for combo in combinations if combo['id'] != combo_id]
    save_combinations()
    await ctx.send(f'Combinaison avec ID {combo_id} supprimée.')

# Commande pour afficher l'aide
@bot.command(name='chelp')
async def show_help(ctx):
    print("Commande chelp reçue")
    help_text = """
    **Commandes disponibles :**
    `!clist` - Affiche toutes les combinaisons disponibles avec leur ID.
    `!cadd [prop1] [prop2]` - Ajoute une combinaison. Si `[prop1]` est écrit, alors `[prop2]` sera envoyé.
    `!cdel [id]` - Supprime la combinaison associée à l'ID spécifié.
    """
    await ctx.send(help_text)

# Gestion des messages pour déclencher une réponse en fonction des combinaisons
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"Message reçu : {message.content}")
    last_word = message.content.split()[-1].lower()
    for combo in combinations:
        if last_word == combo['trigger']:
            print(f"Match trouvé pour {last_word} : réponse avec {combo['response']}")
            await message.channel.send(combo['response'])
            break

    await bot.process_commands(message)  # Assure que les commandes sont bien traitées après la gestion des messages

# Événement lorsque le bot est prêt
@bot.event
async def on_ready():
    # Afficher un message de statut personnalisé
    activity = discord.Game(name="Tapez !chelp pour l'aide")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'{bot.user} est connecté et prêt à l\'action avec le statut !chelp !')

# Démarrage du bot
bot.run('TOKEN')