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

def natural_response(transcribed_text):
    try:
        prompt_text = f"Rispondimi in NLP ai messaggi che ti invio come se fossi un amico virtuale\n{transcribed_text}"
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
        #print(prompt_text)
        return emotion
    except Exception as err:
        print("Error:", err)
        return "Failed"

def detect_emotions(transcribed_text):
    try:
        prompt_text = f"Dato un messaggio come input, Voglio che tu mi risponda in maniera naturale e tra parentesi " \
                      f"quadrate mi metti lo stato d'animo dell'input\n\nGli stati d'animo devo essere scelti tra " \
                      f"i seguenti:\nfelicità\ntristezza\npaura\nrabbia\ncalma\nnessuno stato d'animo\n{transcribed_text}"
        response_emo = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_text,
            temperature=0,
            max_tokens=30,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        emotion = response_emo.choices[0].text.strip()
        print(emotion)
        #print(prompt_text)
        return emotion
    except Exception as err:
        print("Error:", err)
        return "Failed"


def detect_command(transcribed_text):
    emotion = None
    try:
        prompt_text = f"interpreta questo messggio e  inseriscimi:\n1 se l'utente vuole che la luce si spenga.\n2 se l'utente vuole che la luce si accenda\n3 se l'utente vuole che la musica si accenda,\n4 se l'utente vuole che la musica si spenga,\n5 se vuole che una muscia rilassante, \n6 se vuole una musca allegra. \n9 se invece non richiedo nessuna di queste funzioni inserisci 9\n\nutente: Accendimi la luce.\n2\n\nutente: Accendi la luce.\n2\n\nutente: Mi accendi la luce.\n2\n\nutente: Accendi subito la luce.\n2\n\nutente: Ciao mi accenderesti la luce di casa?\n2\n\nutente: mi accendi la lampadina?\n2\n\nutente: Spegnimi la luce.\n1\n\nutente: Spegni la luce per favore.\n1\n\nutente: C'è troppa luce qui le la spegni?\n1\n\nutente: Quanto sole fuori mi spegni la luce?\n1\n\nutente: Si è fatta notte mi accendi subito la luce?\n2\n\nutente: Oggi sono felice?\n3\n\nutente: Ciao come stai?\n9\n\nutente: Oggi non sto tanto bene il mio cane è morto?\n9\n\nutente: Esigo che tu mi accenda all'istante immediato la luce\n1\n\nutente: Mettimi della musica.\n3\n\nutente: Ho voglia di sentire un po di musica.\n3\n\nutente: Mi metti della musica rilassante?\n3\n\nutente: Mettimi subito della musica.\n3\n\nutente: Riproducimi della musica casuale.\n3\n\nutente: Spegnimi la musica\n4\n\nutente: Troppo rumore spegnimi la musica\n4\n\nutente: Mi metti della musica rilassante?\n5\n\nutente: Ho voglia di relax, mettimi della musica.\n5\n\nutente: Ora ci starebbe della musica rilassante\n5\n\nutente: Mi metti della muscia allegra?\n6\n\nutente: Ho voglia di festa mi metti della musica?\n6\n\nutente: Sono in mood party. Mi metti delle canzoni?\n6\n\nutente: Oggi sono triste\n9\n\nutente: Sono molto arrabbiato\n9\n\nutente: Come stai? non trovo le chiavi\n9\n{transcribed_text}?",

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
                message_text = process_voice_messages(file_path)
                command = detect_command(message_text)

                response_text = detect_emotions(message_text)
                moods = re.findall(r'\[(.*?)\]',response_text)  # La parola tra parentesi quadre la salva in una variabile
                response_text = re.sub(r'\[.*?\]', '',response_text)  # Rimuove le parole tra parentesi quadre dalla risposta
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

    return response


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
    if 'felicità' in moods:
        ser.write(b'1')  # Invia il comando
        print("1 - felicità")
    elif 'tristezza' in moods:
        ser.write(b'2')  # Invia il comando
        print("2 - tristezza")
    elif 'paura' in moods:
        ser.write(b'3')  # Invia il comando
    elif 'rabbia' in moods:
        ser.write(b'4')  # Invia il comando


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
