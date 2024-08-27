import discord
import requests
import asyncio
from datetime import datetime

# Ton token de bot Discord et la clé API de la NASA
DISCORD_TOKEN = 'YOURTOKEN'
NASA_API_KEY = 'YOURTOKEN'

# Configuration du client Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Variable pour stocker la dernière date d'image publiée
last_apod_date = None

async def check_and_send_apod(channel):
    global last_apod_date

    # Requête pour obtenir l'image du jour (APOD)
    apod_url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    response = requests.get(apod_url)
    data = response.json()

    # On récupère la date de l'image
    apod_date = data['date']

    # Vérifie si l'image est déjà publiée
    if apod_date != last_apod_date:
        # Créer un embed pour Discord
        embed = discord.Embed(
            title=f"📅 Astronomy Picture of the Day - {apod_date}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Ajout du titre de l'image
        embed.add_field(name="🌌 Titre", value=data['title'], inline=False)
        
        # Limiter l'explication à un certain nombre de caractères pour éviter un bloc de texte trop long
        explanation = data['explanation']
        if len(explanation) > 1024:
            explanation = explanation[:1021] + "..."  # Troncature avec trois points
        embed.add_field(name="📖 Explication", value=explanation, inline=False)
        
        # Crédits et Prochaine Image en ligne
        credits = data.get('copyright', 'Public Domain')
        embed.add_field(name="📝 Crédits", value=credits, inline=True)
        
        # Ajouter l'image actuelle
        embed.set_image(url=data['url'])
        
        # Ajouter une note de bas de page
        embed.set_footer(text="Image publiée par la NASA via l'API APOD")

        # Envoyer l'embed dans le channel
        await channel.send(embed=embed)

        # Mise à jour de la dernière date publiée
        last_apod_date = apod_date

@client.event
async def on_ready():
    print(f'Connecté en tant que {client.user.name}')
    channel = discord.utils.get(client.get_all_channels(), name="apod")

    if channel:
        while True:
            await check_and_send_apod(channel)
            await asyncio.sleep(3600)  # Attendre une heure avant de vérifier à nouveau
    else:
        print("Channel 'apod' introuvable")

client.run(DISCORD_TOKEN)



