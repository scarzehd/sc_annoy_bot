import discord
import dotenv
import os
import asyncio
import random

class MessageCondition:
    def check_condition(self, message:discord.Message) -> bool: return True

class RandomCondition(MessageCondition):
    def __init__(self, chance:float):
        self.chance = chance
    
    def check_condition(self, message):
        if random.random() > self.chance:
            return False
        return True

class TextCondition(MessageCondition):
    def __init__(self, text:str, filter_whitespace:bool = True, filter_case:bool = True, filter_punctuation:bool = True):
        self.text = text
        self.filter_whitespace = filter_whitespace
        self.filter_case = filter_case
        self.filter_punctuation = filter_punctuation
    
    def check_condition(self, message):
        processed = process_string(message.content, self.filter_whitespace, self.filter_case, self.filter_punctuation)
        if self.text in processed:
            return True
        
        return False

class MatchWordCondition(MessageCondition):
    def __init__(self, text:str, filter_case:bool = True, filter_punctuation:bool = True):
        self.text = text
        self.filter_case = filter_case
        self.filter_punctuation = filter_punctuation
    
    def check_condition(self, message):
        processed = process_string(message.content, False, self.filter_case, self.filter_punctuation)
        for word in processed.split():
            if word == self.text:
                return True
        
        return False

class AndCondition(MessageCondition):
    def __init__(self, conditions:list[MessageCondition]):
        self.conditions = conditions
    
    def check_condition(self, message):
        for condition in self.conditions:
            if not condition.check_condition(message):
                return False

        return True

class OrCondition(MessageCondition):
    def __init__(self, conditions:list[MessageCondition]):
        self.conditions = conditions
    
    def check_condition(self, message):
        for condition in self.conditions:
            if condition.check_condition(message):
                return True
        
        return False

class MessageResponse:
    def respond(self, message:discord.Message): pass

class TextResponse(MessageResponse):
    def __init__(self, response:str):
        self.response = response

    def respond(self, message:discord.Message):
        asyncio.create_task(message.reply(self.response))

class EmojiResponse(MessageResponse):
    def __init__(self, emoji_names:list[str]):
        self.emoji_names = emoji_names
    
    def respond(self, message:discord.Message):
        for emoji in message.guild.emojis:
            if emoji.name in self.emoji_names:
                asyncio.create_task(message.add_reaction(emoji))
                return

class MessageHandler:
    def __init__(self, conditions:list[MessageCondition], responses:list[MessageResponse]):
        self.conditions = conditions
        self.responses = responses

    def handle_message(self, message:discord.Message) -> bool:
        handled = False
        for condition in self.conditions:
            if condition.check_condition(message):
                for response in self.responses:
                    response.respond(message)
                handled = True
        
        return handled

less_than_conditions = [
    TextCondition("lessthan"),
    TextCondition("focus"),
    TextCondition("hypnosis"),
    TextCondition("didntnotice"),
    TextCondition("evennotice"),
    TextCondition("oblivion"),
    TextCondition("barelyrecognize"),
    TextCondition("violence")
]

handlers:list[MessageHandler] = [
    MessageHandler(
        [
            AndCondition(
                [
                    RandomCondition(0.7),
                    OrCondition(less_than_conditions)
                ]
            )
        ],
        [
            TextResponse("WHAT ARE YOU WAITING FOR?")
        ]
    ),
    MessageHandler(
        less_than_conditions,
        [
            EmojiResponse("lessthan")
        ]
    ),
    MessageHandler(
        [
            TextCondition("shutup"),
            TextCondition("shutthehellup"),
            TextCondition("shutthefuckup")
        ],
        [
            TextResponse("SILENCE"),
            EmojiResponse("lessthan")
        ]
    ),
    MessageHandler(
        [
            TextCondition("pieces"),
            TextCondition("peices")
        ],
        [
            TextResponse("Put. It. Together.")
        ]
    ),
    MessageHandler(
        [
            AndCondition(
                [
                    TextCondition("annoy"),
                    RandomCondition(0.5)
                ]
            )
        ],
        [
            TextResponse("Stop annoying yourself.")
        ]
    ),
    MessageHandler(
        [
            AndCondition(
                [
                    TextCondition("bot"),
                    RandomCondition(0.35)
                ]
            )
        ],
        [
            TextResponse("I'm not a bot.")
        ]
    ),
    MessageHandler(
        [
            MatchWordCondition("late")
        ],
        [
            TextResponse("https://tenor.com/view/warframe-whispers-in-the-wall-tenno-entrati-1999-gif-16943765476869672917"),
            EmojiResponse("albrecht_entrati")
        ]
    )
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

    for handler in handlers:
        if handler.handle_message(message):
            return

def process_string(string:str, filter_whitespace:bool = True, filter_case:bool = True, filter_punctuation:bool = True) -> str:
    if filter_whitespace:
        string = "".join(string.split())
    
    if filter_case:
        string = string.lower()
    
    if filter_punctuation:
        characters_to_remove = ",.-_;:'\"?\\/|()*&^%$#@!"
        for char in characters_to_remove:
            string = string.replace(char, "")
    
    return string

client.run(api_key)