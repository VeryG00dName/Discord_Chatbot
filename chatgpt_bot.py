import openai
from dotenv import load_dotenv
import os
import json
import discord
from discord.ext import commands

load_dotenv()

openai.api_key = os.environ.get("openai-api")
discord_token = os.environ.get("discord-token")
global pre_prompt
global pre_pre_prompt
global context_limit

BLOCKED_CHANNELS_FILE = "blocked_channels.json"
blocked_channels = {}
# Load the blocked channels from the JSON file
try:
    with open(BLOCKED_CHANNELS_FILE, "r") as f:
        blocked_channels = json.load(f)
except FileNotFoundError:
    blocked_channels = {}

BLOCKED_USERS_FILE = "blocked_users.json"
blocked_users = []

# Load the blocked users from the JSON file
try:
    with open(BLOCKED_USERS_FILE, "r") as f:
        blocked_users = json.load(f)
except FileNotFoundError:
    # Create the file if it doesn't exist
    with open(BLOCKED_USERS_FILE, "w") as f:
        json.dump(blocked_users, f)

context_limit = 5
pre_pre_prompt = ""
pre_prompt = "You are a discord bot chat bot, there are lots of people in the server don't assume everyone is talking to you aspectly if they don't adress it to you!"

totalk=[
    {
        "name": "should_i_talk",
        "description": "tell it whether in the most resent messages if someone is talking to you and if it makes sense for you to talk or not",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "yes or no",
                },
            },
            "required": ["answer"],
        },
    }
]

functions=[
    {
        "name": "set_pre_promp",
        "description": "sets your pre prompt, which is like a guide for future you",
        "parameters": {
            "type": "object",
            "properties": {
                "new_pre_prompt": {
                    "type": "string",
                    "description": "the new pre prompt",
                },
            },
            "required": ["new_pre_prompt"],
        },
    },
    {
        "name": "art",
        "description": "generates an image with a prompt",
        "parameters": {
            "type": "object",
            "properties": {
                "art_prompt": {
                    "type": "string",
                    "description": "prompt to generate art with",
                },
            },
            "required": ["art_prompt"],
        },
    }
]

async def set_pre_promp(pre_prompt):
        global pre_pre_prompt
        pre_pre_prompt = pre_prompt
        await bot.change_presence(activity=discord.Game(name=pre_pre_prompt))
        
async def art(art_prompt,message):
        # Generate the image
        image = openai.Image.create(
	  	prompt=art_prompt,
	    n=2,
        size="512x512"
        )
        # Send the image to the user
        await message.channel.send(image["data"][0]["url"])

class ChatGPTBot(discord.Bot):
    async def on_message(self, message):
        global context_limit
        if str(message.author.id) in blocked_users:
            return
        server_id = str(message.guild.id)
        if server_id in blocked_channels and message.channel.name in blocked_channels[server_id]:
            return
        # Handle incoming messages here
        print(message.author,message.channel,message.content)
        if message.author == self.user:
            return
        message_history = await self.get_message_history(channel=message.channel, limit=context_limit)
        response_message = await get_response_message(message_history)
        await handle_response_message(response_message, message_history, message)

    async def get_message_history(self, channel, limit):
        message_history = []
        async for previous_message in channel.history(limit=limit):
            if previous_message.content == "context block":
                break
            if str(previous_message.author.id) in blocked_users:
                return
            elif previous_message.author != self.user:
                message_history.append({"role": "user", "content": f"{previous_message.author} said {previous_message.content}"})
            else:
                message_history.append({"role": "assistant", "content": previous_message.content})
        if pre_pre_prompt != "":
            message_history.append({"role": "system", "content": pre_pre_prompt})
        if pre_prompt != "":
            message_history.append({"role": "system", "content": pre_prompt})
        message_history.reverse()
        print(message_history)
        return message_history

async def get_response_message(message_history):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=message_history,
        functions=totalk,
        function_call={"name": "should_i_talk"}
)
    response_message = response["choices"][0]["message"]
    print(response)
    return response_message

async def handle_response_message(response_message, message_history, message):
    response_args = json.loads(response_message["function_call"]["arguments"])
    bot_answer = response_args.get("answer")
    if bot_answer == "yes":
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=message_history,
            functions=functions,
            function_call="auto"
        )
        print(response)
        response_message = response["choices"][0]["message"]
        if response_message.get("function_call"):
            available_functions = {
            "set_pre_promp": set_pre_promp,
            "art": art,
            }
            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            if function_to_call.__name__ == "set_pre_promp":
                await function_to_call(pre_prompt=function_args.get("new_pre_prompt"))
            elif function_to_call.__name__ == "art":    
                    await function_to_call(art_prompt=function_args.get("art_prompt"),message=message)
        else:
            await message.channel.send(response.choices[0].message.content)
            
            
bot = ChatGPTBot("!", owner_id=224336385136394240)

@bot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")

@bot.slash_command(name="set_pre_prompt", description="Set the pre_prompt variable")
async def set_pre_prompt(ctx, new_pre_prompt: str):
    global pre_prompt
    pre_prompt = new_pre_prompt
    await ctx.respond(f"pre_prompt has been set to: {pre_prompt}")

@bot.slash_command(name="set_pre_pre_prompt", description="Set the pre_pre_prompt variable")
async def set_pre_pre_prompt(ctx, new_pre_pre_prompt: str):
    global pre_pre_prompt
    pre_pre_prompt = new_pre_pre_prompt
    await ctx.respond(f"pre_pre_prompt has been set to: {pre_pre_prompt}")

@bot.slash_command(name="set_context_limit", description="Set the context_limit variable")
async def set_context_limit(ctx, new_context_limit: int):
    global context_limit
    context_limit = new_context_limit
    await ctx.respond(f"context_limit has been set to: {context_limit}")

@bot.slash_command(name="block_channel", description="Block a channel")
async def block_channel(ctx, channel_name: str):
    if ctx.author.id == bot.owner_id:
        server_id = str(ctx.guild.id)
        # Add the new channel to the list of blocked channels for the server
        if server_id not in blocked_channels:
            blocked_channels[server_id] = []
        blocked_channels[server_id].append(channel_name)

        # Save the updated list of blocked channels to the JSON file
        with open(BLOCKED_CHANNELS_FILE, "w") as f:
            json.dump(blocked_channels, f)

        await ctx.respond(f"Channel '{channel_name}' has been blocked in this server.")

@bot.slash_command(name="block_user", description="Block a user")
async def block_user(ctx, user_id: str):
    if ctx.author.id == bot.owner_id:
        # Add the blocked user to the list
        if user_id not in blocked_users:
            blocked_users.append(user_id)

        # Save the updated list of blocked users to the JSON file
        with open(BLOCKED_USERS_FILE, "w") as f:
            json.dump(blocked_users, f)

        await ctx.respond(f"User with ID '{user_id}' has been blocked.")


bot.run(discord_token)
