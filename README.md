# ChatGPTBot - Discord bot using OpenAI GPT-3.5

This is a Discord bot that uses the OpenAI GPT-3.5 language model to generate responses to messages sent to it. The bot listens for messages in Discord channels and responds to messages that start with `!bot`. It uses the previous 20 messages in the channel (up until a message containing the text `context block`) as input to the GPT-3.5 model to generate a response, which it sends back to the channel. The bot also responds to messages starting with `!pre` by setting a "presence" status on Discord to the text that follows `!pre`, and to messages starting with `!art` by generating an image using the OpenAI DALL-E 2 model.

## Getting started

To get started, you will need to have Python 3.7 or later installed, as well as valid API keys for both OpenAI and Discord. You can obtain an API key for OpenAI from the [OpenAI API website](https://beta.openai.com/docs/api-reference/introduction). To obtain a Discord bot token, you can follow the instructions in the [Discord Developer Portal](https://discord.com/developers/docs/intro).

Once you have obtained your API keys, you can clone this repository to your local machine and install the required Python packages:

 the required Python packages:

shell
Copy code
$ git clone https://github.com/VeryG00dName/Discord_Chatbot.git
$ cd chatgptbot-discord
$ pip install -r requirements.txt

Next, you will need to set your OpenAI and Discord API keys as environment variables. You can do this by creating a new file named `.env` in the root directory of the project, and adding the following lines:


$ python bot.py
## Contributing

Pull requests are welcome! If you would like to contribute to this project, please create a new branch for your changes and submit a pull request. 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.
