import discord
import dotenv
import os
import asyncio

# text_triggers = {
#     "lessthan": "WHAT ARE YOU WAITING FOR?",
#     "didn'tnotice": "WHAT ARE YOU WAITING FOR?",
#     "didntnotice": "WHAT ARE YOU WAITING FOR?",
#     "didn'tevennotice": "WHAT ARE YOU WAITING FOR?",
#     "didntevennotice": "WHAT ARE YOU WAITING FOR?",
#     "oblivion": "WHAT ARE YOU WAITING FOR?",
#     "pieces": "Put. It. Together."
# }

class MessageTrigger:
    def handle_message(self, message:discord.Message):
        pass

class TextTrigger(MessageTrigger):
    def __init__(self, triggers:list[str], response:str):
        self.triggers = triggers
        self.response = response

    def handle_message(self, message:discord.Message):
        processed_string = process_string(message.content)
        if processed_string in self.triggers:
            asyncio.create_task(message.reply(self.response))

class EmojiTrigger(MessageTrigger):
    def __init__(self, triggers:list[str], emoji_names:list[str]):
        self.triggers = triggers
        self.emoji_names = emoji_names
    
    def handle_message(self, message:discord.Message):
        processed_string = process_string(message.content)
        if processed_string in self.triggers:
            for emoji in message.guild.emojis:
                if emoji.name in self.emoji_names:
                    asyncio.create_task(message.add_reaction(emoji))

triggers:list[MessageTrigger] = [
    TextTrigger([
        "lessthan",
        "focus",
        "hypnosis",
        "didntnotice",
        "didntevennotice",
        "oblivion"
    ], "WHAT ARE YOU WAITING FOR?"),
    EmojiTrigger([
        "lessthan",
        "focus",
        "hypnosis",
        "didntnotice",
        "didntevennotice",
        "oblivion"
    ], "lessthan"),
    TextTrigger([
        "pieces",
        "peices"
    ], "Put. It. Together.")
]

dotenv.load_dotenv(".env")

api_key = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print()
    print(f"Logged in as: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    global lessthan
    print(f"Message from {message.author}: {message.content}")
    processed_message = process_string(message.content)
    # if "lessthan" in processed_message or "focus" in processed_message or "oblivion" in processed_message:
    #     if lessthan == None:
    #         lessthan = await message.guild.fetch_emoji(1287978418314547241)
    #         print(lessthan.name)
    #     await message.add_reaction(lessthan)

    for trigger in triggers:
        trigger.handle_message(message)

def process_string(string:str) -> str:
    characters_to_remove = ",.-_;:'\""
    string = "".join(string.lower().split())
    for char in characters_to_remove:
        string = string.replace(char, "")
    return string

print(api_key)

client.run(api_key)