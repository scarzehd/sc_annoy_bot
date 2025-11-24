import discord
import dotenv
import os
import asyncio
import random

class MessageTrigger:
    def handle_message(self, message:discord.Message):
        pass

class TextTrigger(MessageTrigger):
    def __init__(self, triggers:list[str], response:str):
        self.triggers = triggers
        self.response = response

    def handle_message(self, message:discord.Message):
        processed_string = process_string(message.content)
        for trigger in self.triggers:
            if trigger in processed_string:
                asyncio.create_task(message.reply(self.response))
                return

class RandomTrigger(MessageTrigger):
    def __init__(self, chance:float, trigger:MessageTrigger):
        self.chance = chance
        self.trigger = trigger
    
    def handle_message(self, message):
        if random.random() > self.chance:
            return
        self.trigger.handle_message(message)

class EmojiTrigger(MessageTrigger):
    def __init__(self, triggers:list[str], emoji_names:list[str]):
        self.triggers = triggers
        self.emoji_names = emoji_names
    
    def handle_message(self, message:discord.Message):
        processed_string = process_string(message.content)
        for trigger in self.triggers:
            if trigger in processed_string:
                for emoji in message.guild.emojis:
                    if emoji.name in self.emoji_names:
                        asyncio.create_task(message.add_reaction(emoji))
                        return

triggers:list[MessageTrigger] = [
    RandomTrigger(0.5,
        TextTrigger([
            "lessthan",
            "focus",
            "hypnosis",
            "didntnotice",
            "evennotice",
            "oblivion",
            "barelyrecognize"
        ], "WHAT ARE YOU WAITING FOR?")
    ),
    EmojiTrigger([
        "lessthan",
        "focus",
        "hypnosis",
        "didntnotice",
        "evennotice",
        "oblivion",
        "barelyrecognize"
    ], "lessthan"),
    TextTrigger([
        "pieces",
        "peices"
    ], "Put. It. Together."),
    RandomTrigger(0.25, 
        TextTrigger([
            "annoy"
        ], "Stop annoying yourself.")
    ),
    RandomTrigger(0.15, 
        TextTrigger([
            "bot"
        ], "I'm not a bot.")
    ),
]

dotenv.load_dotenv(".env")

api_key = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f"Message from {message.author}: {message.content}")

    for trigger in triggers:
        trigger.handle_message(message)

def process_string(string:str) -> str:
    characters_to_remove = ",.-_;:'\"?\\/|()*&^%$#@!"
    string = "".join(string.lower().split())
    for char in characters_to_remove:
        string = string.replace(char, "")
    return string

client.run(api_key)