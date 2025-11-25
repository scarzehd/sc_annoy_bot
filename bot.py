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
    def __init__(self, text:str):
        self.text = text
    
    def check_condition(self, message):
        processed = process_string(message.content)
        if self.text in processed:
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

    def handle_message(self, message:discord.Message):
        for condition in self.conditions:
            if condition.check_condition(message):
                for response in self.responses:
                    response.respond(message)
                return

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
            TextCondition("shutup")
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
    )
    # RandomTrigger(0.5,
    #     TextTrigger([
    #         "lessthan",
    #         "focus",
    #         "hypnosis",
    #         "didntnotice",
    #         "evennotice",
    #         "oblivion",
    #         "barelyrecognize",
    #         "justify"
    #     ], "WHAT ARE YOU WAITING FOR?")
    # ),
    # EmojiTrigger([
    #     "lessthan",
    #     "focus",
    #     "hypnosis",
    #     "didntnotice",
    #     "evennotice",
    #     "oblivion",
    #     "recognize",
    #     "justify"
    # ], "lessthan"),
    # TextTrigger([
    #     "pieces",
    #     "peices"
    # ], "Put. It. Together."),
    # RandomTrigger(0.25, 
    #     TextTrigger([
    #         "annoy"
    #     ], "Stop annoying yourself.")
    # ),
    # RandomTrigger(0.15, 
    #     TextTrigger([
    #         "bot"
    #     ], "I'm not a bot.")
    # ),
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
        handler.handle_message(message)

def process_string(string:str) -> str:
    characters_to_remove = ",.-_;:'\"?\\/|()*&^%$#@!"
    string = "".join(string.lower().split())
    for char in characters_to_remove:
        string = string.replace(char, "")
    return string

client.run(api_key)