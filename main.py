import os
import logging
import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.utils.request import Request
import openai
# local imports:
import env
from convert import convert_to_mp3
# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

media_file_path = "./"
model_id = "whisper-1"
bot_token = env.bot_token
API_KEY = env.API_KEY
openai.api_key = env.API_KEY


def get_openai_response(message_text):
    prompt_text = f"Dato un messaggio come input, Voglio che tu mi risponda in maniera naturale e tra parentesi " \
                  f"quadrate mi metti lo stato d'animo dell'input\n\nGli stati d'animo devo essere scelti tra " \
                  f"i seguenti:\nFelicità\nTristezza\nPaura\nRabbia\nCalma\n{message_text}?"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_text,
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return response.choices[0].text.strip()


def voice_handler(update, context):
    voice_file = update.message.voice
    # Get file path on Telegram server
    file = context.bot.get_file(voice_file.file_id)
    url = file.file_path
    print(url)

    response = requests.get(url)
    print(response)
    # Save the voice message
    folder_path = media_file_path
    file_name = f"{voice_file.file_id}.ogg"
    file_path = os.path.join(folder_path, file_name)

    try:
        #save the downloaded audio file
        with open(file_path, 'wb') as f:
            f.write(response.content)
            print("SAVED VOICE MESSAGE - as ogg")
            # Send a confirmation message
            context.bot.send_message(chat_id=update.effective_chat.id, text="Voice message saved.")
            try:
                #Try process emotion then send to chat.
                emotion = process_voice_messages(file_path)
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"{emotion}")
            except Exception as e:
                print("Error:", e)
    except Exception as e:
        print("Error:", e)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Error occurred while saving the voice message.")


def process_voice_messages(file_path):
    convert_to_mp3(file_path)
    os.remove(file_path)
    mp3_file = file_path + ".mp3"
    media_file = open(mp3_file, "rb")
    print("Opening File: " + file_path)
    # ['m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg']
    # Transcribe the audio
    response = openai.Audio.transcribe(
        api_key=API_KEY,
        model=model_id,
        file=media_file,
        response_format='text'  # text, json, srt, vtt
    )
    print(str(response))
    os.remove(mp3_file)
    # Detect emotions from the transcription
    emotions = detect_emotions(response)
    return emotions


def detect_emotions(transcribed_text):
    emotion = None
    try:
        prompt_text = f"Dato un messaggio come input, Voglio che tu mi risponda in maniera naturale e tra parentesi " \
                      f"quadrate mi metti lo stato d'animo dell'input\n\nGli stati d'animo devo essere scelti tra " \
                      f"i seguenti:\nFelicità\nTristezza\nPaura\nRabbia\nCalma\n{transcribed_text}?"
        response_emo = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_text,
            temperature=0,
            max_tokens=64,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        emotion = response_emo.choices[0].text.strip()
        print(emotion)
        return emotion
    except Exception as err:
        print("Error:", err)
        return "Failed"

# Function to handle start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ciao! Sono un bot Telegram. "
                                                                    "Inviami un messaggio o un messaggio vocale.")

# Function to handle text messages
def echo(update, context):
    message_text = update.message.text
    response_text = get_openai_response(message_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

# Set up the bot
request = Request(con_pool_size=20)
bot = telegram.Bot(token=bot_token, request=request)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher

# Register handlers
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(MessageHandler(Filters.text, echo))
dispatcher.add_handler(MessageHandler(Filters.voice, voice_handler))

# Start the bot
updater.start_polling()
updater.idle()
