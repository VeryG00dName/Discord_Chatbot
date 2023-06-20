from dotenv import load_dotenv
import openai
import discord
import os
import json
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
openai.api_key = os.environ.get("openai-api")
discord_token = os.environ.get("discord-token")
global pre_prompt
global pre_pre_prompt
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
        "description": "sets your pre prompt",
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

class ChatGPTBot(commands.Bot):
    async def on_message(self, message):
        global pre_prompt
        global pre_pre_prompt
        # Handle incoming messages here
        print(message.author,message.channel,message.content)
        if message.author == self.user:
            return
        
        else:
            print('test')
            # This is a message intended for the bot, so we can respond
            # Retrieve the previous messages in the current channel
            channel = message.channel
            message_history = []
            async for previous_message in channel.history(limit=5):
                # Add the previses messeges to the message history
                # print(message_history)
                if previous_message.content == "context block":
                    break
                if previous_message.author != self.user:
                    message_history.append({"role": "user", "content": str(previous_message.author) + " said " + previous_message.content})
                else:
                    message_history.append({"role": "assistant", "content": previous_message.content})
            # message_history.reverse()
            if pre_pre_prompt != "":
                message_history.append({"role": "system", "content": pre_pre_prompt})
            message_history.append({"role": "system", "content": pre_prompt})
            # Use the message history as input for the chatbot
            message_history.reverse()
            print(message_history)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=message_history,
                functions=totalk,
                function_call={"name": "should_i_talk"}
            )

            response_message = response["choices"][0]["message"]
            print(response)
            # Check if GPT wanted to call a function
            
            response_args = json.loads(response_message["function_call"]["arguments"])
            bot_answer=response_args.get("answer")

            if bot_answer == "yes":
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-0613",
                    messages=message_history,
                    functions=functions,
                    function_call="auto"
                )

                response_message = response["choices"][0]["message"]
                print(response_message)

                if response_message.get("function_call"):
                    available_functions = {
                    "set_pre_promp": set_pre_promp,
                    "art": art,
                    }
                    function_name = response_message["function_call"]["name"]
                    fuction_to_call = available_functions[function_name]
                    function_args = json.loads(response_message["function_call"]["arguments"])
                    print(fuction_to_call)
                    if fuction_to_call.__name__ == "set_pre_promp":
                        await fuction_to_call(pre_prompt=function_args.get("new_pre_prompt"))
                    elif fuction_to_call.__name__ == "art":    
                            await fuction_to_call(art_prompt=function_args.get("art_prompt"),message=message)
                else:
                    await message.channel.send(response.choices[0].message.content) 
            
bot = ChatGPTBot("!",intents=intents)
bot.run(discord_token)
