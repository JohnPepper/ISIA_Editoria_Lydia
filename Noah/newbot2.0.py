import os
import logging
import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.request import Request
import openai
from pydub import AudioSegment
import asyncio
import base64

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

async def convert_to_mp3_async(ogg_path, mp3_path):
    sound = AudioSegment.from_file(ogg_path, format="ogg")
    sound.export(mp3_path, format="mp3", bitrate="128k")

def handle_voice(update, context):
    # Recupera il file vocale
    voice_file = context.bot.get_file(update.message.voice.file_id)

    # Scarica il file vocale in formato .ogg
    ogg_path = f"{update.message.voice.file_id}.ogg"
    voice_file.download(ogg_path)

    # Converte il file audio in formato .mp3 in modo asincrono
    mp3_path = os.path.join(os.getcwd(), f"{update.message.voice.file_id}.mp3")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(convert_to_mp3_async(ogg_path, mp3_path))

    # Verifica che il file .mp3 sia stato creato
    if not os.path.exists(mp3_path):
        context.bot.send_message(chat_id=update.message.chat_id, text="Si è verificato un errore durante la conversione del file audio.")
        return

    # Legge il file audio in formato .mp3
    with open(mp3_path, "rb") as f:
        audio_bytes = f.read()

    # Converti i dati binari in una stringa base64
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

    # Chiama l'API di Whisper-1 per ottenere la risposta
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Dato un messaggio vocale come input, voglio che tu mi risponda in maniera naturale.",
        temperature=0.5,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        inputs={
            "voice": audio_base64,
            "model": model_id,
        },
    )

    # Invia la risposta al mittente del messaggio vocale
    context.bot.send_message(chat_id=update.message.chat_id, text=response.choices[0].text)

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, echo))

dispatcher.add_handler(MessageHandler(Filters.voice, handle_voice))
updater.start_polling()
updater.idle()

