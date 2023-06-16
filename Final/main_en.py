import os
import logging
import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.utils.request import Request
import openai
import re
import serial

# local imports:
import env
from convert import convert_to_mp3

# Set up serial
# ser = serial.Serial('/dev/cu.SLAB_USBtoUART', 115200)
ser = serial.Serial('/dev/cu.usbserial-14130', 9600)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

media_file_path = "./"
model_id = "whisper-1"
bot_token = env.bot_token
API_KEY = env.API_KEY
openai.api_key = env.API_KEY


def detect_emotions(transcribed_text):
    emotion = None
    try:
        prompt_text = f"Given a message as input, I want you to respond naturally and in square brackets put me the mood of the input\nThe moods must be chosen from the following:\nhappiness,\nsadness,\nfear,\ncalm,\ncalm\nno mood\n\n{transcribed_text}?",
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


def detect_command(transcribed_text):
    emotion = None
    try:
        prompt_text = f"Given a message as input, I want you to respond to me naturally and put the mood of the input in square brackets. The moods must be chosen from the following:\nhappiness\nsadness\nfear\nanger\ncalm\nno mood\n\nUser: Turn on the light for me.\n2\n\nUser: Can you turn on the light?\n2\n\nUser: Could you turn on the light for me?\n2\n\nUser: Turn on the light right away.\n2\n\nUser: Hi, could you turn on the lights in the house?\n2\n\nUser: Can you turn on the light bulb for me?\n2\n\nUser: Turn off the light for me.\n1\n\nUser: Could you please turn off the light?\n1\n\nUser: It's too bright in here, can you turn off the light?\n1\n\nUser: It's so sunny outside, can you turn off the light?\n1\n\nUser: It's night already, can you turn on the light right away?\n2\n\nUser: Today I'm happy\n3\n\nUser: Hi, how are you?\n9\n\nUser: Today I'm not feeling well, my dog died?\n9\n\nUser: I demand that you turn on the light immediately.\n1\n\nUser: Play some music for me.\n3\n\nUser: I feel like listening to some music.\n3\n\nUser: Can you play some relaxing music for me?\n3\n\nUser: Play music for me right now.\n3\n\nUser: Play some random music for me.\n3\n\nUser: Turn off the music for me.\n4\n\nUser: It's too noisy, turn off the music.\n4\n\nUser: Can you play some relaxing music for me?\n5\n\nUser: I feel like relaxing, can you play some music for me?\n5\n\nUser: Some relaxing music would be nice right now.\n5\n\nUser: Can you play some happy music for me?\n6\n\nUser: I feel like partying, can you play some music?\n6\n\nUser: I'm in the mood for partying. Can you play some songs?\n6\n\nUser: Today I'm feeling sad.\n9\n\nUser: I'm very angry.\n9\n\nUser: How are you? I can't find my keys.\n9\n{transcribed_text}?",

        response_emo = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_text,
            temperature=0,
            max_tokens=10,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        #risposta testuale
        command = response_emo.choices[0].text.strip()
        print(command)
        return command
    except Exception as err:
        print("Error:", err)
        return "Failed"


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
                emotion = process_voice_messages(file_path)
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"{emotion}")


            except Exception as e:
                print("Error:", e)
    except Exception as e:
        print("Error:", e)
        context.bot.send_message(chat_id=update.effective_chat.id,text="Error occurred while saving the voice message.")


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

    moods = re.findall(r'\[(.*?)\]', emotions)  # La parola tra parentesi quadre la salva in una variabile
    emotions = re.sub(r'\[.*?\]', '', emotions)  # Rimuove le parole tra parentesi quadre dalla risposta
    execute_action(moods)  # Invia il comando all'ESP32 in base allo stato d'animo
    print(f"Mood: {moods}")
    return emotions


# Function to handle text messages
# Function to handle text messages
def echo(update, context):
    message_text = update.message.text
    command = detect_command(message_text)

    response_text = detect_emotions(message_text)
    moods = re.findall(r'\[(.*?)\]', response_text)  # La parola tra parentesi quadre la salva in una variabile
    response_text = re.sub(r'\[.*?\]', '', response_text)  # Rimuove le parole tra parentesi quadre dalla risposta
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

    if command == '1':
        ser.write(b'5')  # Invia il comando per spegnere la luce
        print("Light OFF")

    elif command == '2':
        ser.write(b'6')  # Invia il comando per accendere la luce
        print("Light ON")

    elif command == '3':
        ser.write(b'7')  # Invia il comando per spegnere la luce
        print("Music ON")

    elif command == '4':
        ser.write(b'8')  # Invia il comando per accendere la luce
        print("Music OFF")

    elif command == '5':
        ser.write(b'9')  # Invia il comando per spegnere la luce
        print("Relaxing music ON")

    elif command == '6':
        ser.write(b'10')  # Invia il comando per accendere la luce
        print("Party music ON")

    else:
        execute_action(moods)  # Invia il comando all'ESP32 in base allo stato d'animo
        print(moods)



def execute_action(moods):
    if 'happiness' in moods:
        ser.write(b'1')  # Invia il comando
        print("1 - happiness")
    elif 'sadness' in moods:
        ser.write(b'2')  # Invia il comando
        print("2 - sadness")
    elif 'fear' in moods:
        ser.write(b'3')  # Invia il comando
        print("2 - fear")
    elif 'anger' in moods:
        ser.write(b'4')  # Invia il comando
        print("2 - anger")


# Set up the bot
request = Request(con_pool_size=20)
bot = telegram.Bot(token=bot_token, request=request)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher

# Register handlers
dispatcher.add_handler(MessageHandler(Filters.text, echo))
dispatcher.add_handler(MessageHandler(Filters.voice, voice_handler))

# Start the bot
updater.start_polling()
updater.idle()
