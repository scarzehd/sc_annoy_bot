import discord
import dotenv

text_triggers = {
    "lessthan": "WHAT ARE YOU WAITING FOR?",
    "didn'tnotice": "WHAT ARE YOU WAITING FOR?",
    "didntnotice": "WHAT ARE YOU WAITING FOR?",
    "didn'tevennotice": "WHAT ARE YOU WAITING FOR?",
    "didntevennotice": "WHAT ARE YOU WAITING FOR?",
    "pieces": "Put. It. Together."
}

lessthan = None



api_key = dotenv.dotenv_values(".env")["DISCORD_BOT_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print()
    print(f"Logged in as: {client.user}")

@client.event
async def on_message(message):
    global lessthan
    print(f"Message from {message.author}: {message.content}")
    processed_message = process_string(message.content)
    if "lessthan" in processed_message or "focus" in processed_message:
        if lessthan == None:
            lessthan = await message.guild.fetch_emoji(1287978418314547241)
        await message.add_reaction(lessthan)
    
    for trigger in text_triggers:
        if trigger in processed_message:
            await message.reply(text_triggers[trigger])
    

def process_string(string:str) -> str:
    return "".join(string.lower().split())



client.run(api_key)