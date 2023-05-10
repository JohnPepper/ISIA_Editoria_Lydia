import telebot
import openai
import os
import tempfile
from urllib.request import urlretrieve
import os
import logging
import requests
from requests.adapters import HTTPAdapter
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.request import Request
import openai
import re

API_TOKEN = '6149818994:AAEu2QDUHTvgJ61SN3fENN7efxQP_neTzKI'
OPENAI_API_KEY = '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'

# Initialize Telegram bot
bot = telebot.TeleBot(API_TOKEN)

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

model_id = "whisper-1"

# Initialize the bot with the custom Request object
bot_token = '6149818994:AAEu2QDUHTvgJ61SN3fENN7efxQP_neTzKI'
bot = telegram.Bot(token=bot_token, request=Request)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def handle_voice_message(message):
    # Download the voice message
    file_info = bot.get_file(message.voice.file_id)
    file_url = f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}'
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        urlretrieve(file_url, temp_file.name)
        with open(temp_file.name, 'rb') as media_file:
            # Transcribe the voice message
            transcription = transcribe_audio(media_file)

    # Analyze the emotion in the transcribed text
    emotion_analysis = analyze_emotion(transcription)

    # Send the emotion analysis as a text message
    bot.send_message(message.chat.id, emotion_analysis)

    # Remove the temporary file from the server's local storage
    os.remove(temp_file.name)

def transcribe_audio(media_file):
    response = openai.Audio.transcribe(
        api_key=OPENAI_API_KEY,
        model=model_id,
        file=media_file,
        response_format='srt'
    )
    return response

def get_openai_response(message_text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Reply on my messages like my friend {message_text}?",
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\"\"\""]
    )
    return response.choices[0].text.strip()

def analyze_emotion(transcribed_text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Analyze the emotion in the following text and give a response in one sentence: {transcribed_text}",
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\"\"\""]
    )
    return response.choices[0].text.strip()

    @bot.message_handler(commands=['help', 'start'])
    def send_welcome(message):
        bot.reply_to(message, """\
        Benvenuto nel primo BOT di prova
        """)

    @bot.message_handler(content_types=['text', 'voice'])
    def handle_message(message):
        if message.content_type == 'text':
            # Handle text messages
            response = get_openai_response(message.text)
            bot.reply_to(message, response)
        elif message.content_type == 'voice':
            # Handle voice messages
            handle_voice_message(message)


bot.polling()