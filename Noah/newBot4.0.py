import os
import logging
import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.request import Request
import openai

# local imports:
from convert import convert_to_mp3
import env

API_TOKEN = env.API_TOKEN
OPENAI_API_KEY = env.OPENAI_API_KEY

model_id = "whisper-1"

openai.api_key = OPENAI_API_KEY

# Create a custom Request object with an increased connection pool size
request = Request(con_pool_size=20)

# Initialize the bot with the custom Request object
bot = telegram.Bot(token=API_TOKEN, request=request)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher

#
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
media_file_path = "./"


def get_openai_response(message_text):
    prompt_text = f"It is the prompt aimed to control Smart home via telegram bot. \nReply to the user as a friend, in the same language the user is using.\n\nTo control their Smart Home the user can mention commands like:\n\n- \"Turn on the lights: warm/cold light, white/red/blue/yellow colour, intensity from 10% to 100%.\"\n- \"Turn on the music: calm, melancholic, happy, energetic, relaxing.\"\n\nDetect those commands, analyse user’s messages and detect emotions. If an emotion is detected, suggest corresponding settings for the Smart Home. If the user expresses feelings or state of being, respond accordingly and adjust the Smart Home settings for his comfort.\n\nThe format of the response should look like this, with detected emotions, commands and settings displayed first:\nUser: \"I'm a little tired today.\"\nBot: \"[Fatigue], (No command), [Light: Soft, warm/yellow, 50% intensity], [Music: Relaxing music]. Oh, I see. You're a little tired today. I set the lights to soft, warm/yellow, 50% intensity. I have also prepared relaxing music for you to help you relax and regenerate. Take care of yourself and try to rest when you can!\"\n\nDetected emotions and corresponding settings:\n\n[Happiness] Lights: Set lights to warm, orange, 100% intensity.\n[Happiness] Music: Play a happy song.\n\n[Sadness] Lights: Set lights to soft, cool/blue, 50% intensity.\n[Sadness] Music: Play a melancholic song.\n\n[Anger] Lights: Set lights to intense, red/violet, 100% intensity.\n[Anger] Music: Play an energetic song.\n\n[Fear] Lights: Set lights to soft, warm/white, 50% intensity.\n[Fear] Music: Play calming music.\n\n[Calmness] Lights: Set lights to neutral/white/blue, 70% intensity.\n[Calmness] Music: Play calming music.\n\n[Fatigue] Lights: Set lights to soft, warm/yellow, 50% intensity.\n[Fatigue] Music: Play relaxing music.\n{message_text}?",

    # prompt_text = f"Dato un messaggio come input, Voglio che tu mi risponda in maniera naturale e tra parentesi quadrate mi metti lo stato d'animo dell'input\n\nGli stati d'animo devo essere scelti tra i seguenti:\nFelicità\nTristezza\nPaura\nRabbia\nCalma\n{message_text}?"
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


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ciao! Sono un bot Telegram.")


def echo(update, context):
    message_text = update.message.text
    response_text = get_openai_response(message_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)


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
        # save the downloaded audio file
        with open(file_path, 'wb') as f:
            f.write(response.content)
            print("SAVED VOICE MESSAGE - as ogg")
            # Send a confirmation message
            context.bot.send_message(chat_id=update.effective_chat.id, text="Voice message saved.")
            try:
                # Try process emotion then send to chat.
                emotion = get_openai_response()
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"Detected emotion: {emotion}")
            except:
                print("failed")
    except Exception as e:
        print("Error:", e)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Error occurred while saving the voice message.")


def process_voice_messages():
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
                api_key=API_TOKEN,
                model="whisper-1",
                file=media_file,
                response_format='text'  # text, json, srt, vtt
            )
            print(str(response))
            os.remove(mp3_file)
            # Detect emotions from the transcription
            emotions = get_openai_response(response)
            return emotions


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, echo))

voice_handler = MessageHandler(Filters.voice, voice_handler)
dispatcher.add_handler(voice_handler)

updater.start_polling()
updater.idle()
