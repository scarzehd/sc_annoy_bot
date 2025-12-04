import discord
import dotenv
import os
import asyncio
import random
import json
from collections.abc import Callable

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
    def __init__(self, conditions:list[MessageCondition], responses:list[MessageResponse], blocking:bool = True):
        self.conditions = conditions
        self.responses = responses
        self.blocking = blocking

    def handle_message(self, message:discord.Message) -> bool:
        handled = False
        for condition in self.conditions:
            if condition.check_condition(message):
                for response in self.responses:
                    response.respond(message)
                handled = True
                break
        
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

class ConfigLoader():
    def load_and_condition(self, data) -> AndCondition:
        conditions:list[TextCondition] = []
        for condition_data in data["conditions"]:
            conditions.append(self.load_condition(condition_data))
        
        return AndCondition(conditions)

    def load_or_condition(self, data) -> OrCondition:
        conditions:list[TextCondition] = []
        for condition_data in data["conditions"]:
            conditions.append(self.load_condition(condition_data))
        
        return OrCondition(conditions)

    def load_text_condition(self, data) -> TextCondition:
        text = data["text"]

        filter_whitespace = True
        if "filter_whitespace" in data:
            filter_whitespace = data["filter_whitespace"]
        
        filter_case = True
        if "filter_case" in data:
            filter_case = data["filter_case"]

        filter_punctuation = True
        if "filter_punctuation" in data:
            filter_punctuation = data["filter_punctuation"]
        
        return TextCondition(text, filter_whitespace, filter_case, filter_punctuation)

    def load_random_condition(self, data) -> RandomCondition:
        chance = data["chance"]
        return RandomCondition(chance)

    def load_match_word_condition(self, data) -> MatchWordCondition:
        text = data["text"]
        filter_case = True
        if "filter_case" in data:
            filter_case = data["filter_case"]

        filter_punctuation = True
        if "filter_punctuation" in data:
            filter_punctuation = data["filter_punctuation"]
        
        return MatchWordCondition(text, filter_case, filter_punctuation)

    conditions:dict[str, Callable] = {
        "text": load_text_condition,
        "match_word": load_match_word_condition,
        "random": load_random_condition,
        "and": load_and_condition,
        "or": load_or_condition
    }

    def load_condition(self, data) -> MessageCondition:
        return self.conditions[data["type"]](self, data)

    def load_text_response(self, data) -> TextResponse:
        return TextResponse(data["text"])

    def load_emoji_response(self, data) -> EmojiResponse:
        return EmojiResponse(data["emoji"])

    responses:dict[str, Callable] = {
        "text": load_text_response,
        "emoji": load_emoji_response
    }

    def load_response(self, data) -> MessageResponse:
        return self.responses[data["type"]](self, data)

    def load_handler(self, data) -> MessageHandler:
        conditions:list[MessageCondition] = []
        for condition_data in data["conditions"]:
            conditions.append(self.load_condition(condition_data))
        
        responses:list[MessageResponse] = []
        for response_data in data["responses"]:
            responses.append(self.load_response(response_data))
        
        blocking = True
        if "blocking" in data:
            blocking = data["blocking"]
        
        return MessageHandler(conditions, responses, blocking)

    def load_config_from_file(self, path:str) -> list[MessageHandler]:
        with open(path) as file:
            config_dict = json.load(file)
            handlers:list[MessageHandler] = []
            for data in config_dict["message_handlers"]:
                handlers.append(self.load_handler(data))
            
            return handlers

loader = ConfigLoader()
handlers:list[MessageHandler] = loader.load_config_from_file("./config.json")
# [
#     MessageHandler(
#         less_than_conditions,
#         [
#             EmojiResponse("lessthan"),
#             TextResponse("WHAT ARE YOU WAITING FOR?")
#         ]
#     ),
#     MessageHandler(
#         [
#             TextCondition("shutup"),
#             TextCondition("shutthehellup"),
#             TextCondition("shutthefuckup")
#         ],
#         [
#             TextResponse("SILENCE"),
#             EmojiResponse("lessthan")
#         ]
#     ),
#     MessageHandler(
#         [
#             TextCondition("pieces"),
#             TextCondition("peices")
#         ],
#         [
#             TextResponse("Put. It. Together.")
#         ]
#     ),
#     MessageHandler(
#         [
#             AndCondition(
#                 [
#                     TextCondition("annoy"),
#                     RandomCondition(0.5)
#                 ]
#             )
#         ],
#         [
#             TextResponse("Stop annoying yourself.")
#         ]
#     ),
#     MessageHandler(
#         [
#             AndCondition(
#                 [
#                     TextCondition("bot"),
#                     RandomCondition(0.35)
#                 ]
#             )
#         ],
#         [
#             TextResponse("I'm not a bot.")
#         ]
#     ),
#     MessageHandler(
#         [
#             MatchWordCondition("late")
#         ],
#         [
#             TextResponse("https://tenor.com/view/warframe-whispers-in-the-wall-tenno-entrati-1999-gif-16943765476869672917"),
#             EmojiResponse("albrecht_entrati")
#         ]
#     )
# ]

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
        if handler.handle_message(message) and handler.blocking:
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