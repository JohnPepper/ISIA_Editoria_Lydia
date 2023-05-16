import os
import logging
import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.request import Request
import openai


#local imports:
import env
from convert import convert_to_mp3

# Set OpenAI API key and Whisper model ID
openai.api_key = env.API_KEY
model_id = "whisper-1"

# Create a custom Request object with an increased connection pool size
request = Request(con_pool_size=20)

# Initialize the bot with the custom Request object
bot_token = env.bot_token
bot = telegram.Bot(token=bot_token, request=request)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

media_file_path = "./"


# Function to handle voice messages
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
                                         text=f"Detected emotion: {emotion}")
            except:
                print("failed")
    except Exception as e:
        print("Error:", e)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Error occurred while saving the voice message.")


# Function to handle start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Send me a voice message and I'll save it.")


def process_voice_messages(file_path):
    for filename in os.listdir(media_file_path):
        if filename.endswith(".ogg"):
            # Open the file
            file_path = os.path.join(media_file_path, filename)
            convert_to_mp3(file_path)
            os.remove(file_path)
            mp3_file = file_path + ".mp3"
            media_file = open(mp3_file, "rb")
            print("Opening File: " + file_path)
            # ['m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg']
            # Transcribe the audio
            response = openai.Audio.transcribe(
                api_key=env.API_KEY,
                model="whisper-1",
                file=media_file,
                response_format='text'  # text, json, srt, vtt
            )
            print(str(response))
            os.remove(mp3_file)
            # Detect emotions from the transcription
            emotions = detect_emotions(response)
            return emotions


def detect_emotions(transcribed_text):
    # your existing code for detecting emotions
    emotion = None
    try:
        prompt = f"Analyse the text, choose an appropriate emotion from the main ones: sadness, happiness, fear, " \
                 f"anger, calm and give the answer in one word:\n\nText: {transcribed_text}\n\nEmotion: "

        response_emo = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.5,
        )

        emotion = response_emo.choices[0].text.strip()
        print(emotion)
        return emotion
    except Exception as err:
        print("Error:", err)
        return "Failed"

######################################################################
# Register handlers
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

voice_handler = MessageHandler(Filters.voice, voice_handler)
dispatcher.add_handler(voice_handler)

# Start the bot
updater.start_polling()
updater.idle()