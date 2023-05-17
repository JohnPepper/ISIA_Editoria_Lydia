import os
import logging
import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.request import Request
import openai
from pydub import AudioSegment

import env

API_TOKEN = env.API_TOKEN
OPENAI_API_KEY = env.OPENAI_API_KEY



# Set OpenAI API key and Whisper model ID
openai.api_key = env.OPENAI_API_KEY
model_id = "whisper-1"

# Create a custom Request object with an increased connection pool size
request = Request(con_pool_size=20)

# Initialize the bot with the custom Request object
bot_token = env.API_TOKEN
bot = telegram.Bot(token=bot_token, request=request)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher


def get_openai_response(message_text):
    prompt_text = f"Dato un messaggio come input, Voglio che tu mi risponda in maniera naturale\n{message_text}?"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_text,
        temperature=0,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return response.choices[0].text.strip()

def convert_to_mp3(file_path):
    sound = AudioSegment.from_file(file_path, format="ogg")
    sound.export(f"{file_path}.mp3", format="mp3", bitrate="128k")

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ciao! Sono un bot Telegram.")

def echo(update, context):
    message_text = update.message.text
    response_text = get_openai_response(message_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, echo))

updater.start_polling()
updater.idle()