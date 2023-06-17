import os
import logging
import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.utils.request import Request
import openai
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
        prompt = f"You are a bot and you have to respond to me in an NLP way as if I were a friend to the messages I send you\n\n" \
                 f"{transcribed_text}\n\n",

        response_emo = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=64,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        nlpresponse = response_emo.choices[0].text.strip()
        print("natural_response: " + nlpresponse)
        return nlpresponse
    except Exception as err:
        print("Error:", err)
        return "Failed"

def detect_emotions(transcribed_text):
    try:
        prompt = f"Given a message as input I want you to parse it and identify one of these moods to me.\n" \
                 f"If it has no mood state you give me as output \"no mood\"\n" \
                 f"The possible moods are as follows:\n" \
                 f"happiness,\n" \
                 f"sadness,\n" \
                 f"anger,\n" \
                 f"tranquility\n\n" \
                 f"Input: Hello how are you?\nno mood\n\n" \
                 f"Input: How much is the square root of 4?\nno mood\n\n" \
                 f"{transcribed_text}\n\n",

        response_emo = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=30,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        emotion = response_emo.choices[0].text.strip()
        print("detect_emotions: " + emotion)
        return emotion
    except Exception as err:
        print("Error:", err)
        return "Failed"

def detect_command(transcribed_text):
    try:
        prompt = f"interpret this messaging and insert:\n" \
                 f"1 if the user wants the light to go out.\n" \
                 f"2 if the user wants the light to come on.\n" \
                 f"3 if the user wants the music to come on,\n" \
                 f"4 if the user wants the music to go off,\n" \
                 f"5 if the user wants a soothing music, \n" \
                 f"6 if he wants upbeat music. \n" \
                 f"9 if instead I do not require any of these functions enter 9\n\n" \
                 f"user: Turn on the light.\n2\n\n" \
                 f"user: Turn on my light.\n2\n\n" \
                 f"user: Turn on the light now.\n2\n\n" \
                 f"user: Hi would you turn on my house light for me?\n2\n\n" \
                 f"user: will you turn on the light bulb for me?\n2\n\n" \
                 f"user: turn off my light.\n1\n\nuser: Turn off the light please.\n1\n\n" \
                 f"user: Is there too much light here will you turn it off?\n1\n\n" \
                 f"user: How much sun outside will you turn off the light for me?\n1\n\n" \
                 f"user: It's gotten dark will you turn the light on me now?\n2\n\n" \
                 f"user: Am I happy today?\n3\n\nuser: Hello how are you?\n9\n\n" \
                 f"user: Today I'm not so good my dog died?\n9\n\n" \
                 f"user: I demand that you turn on my light instantly\n1\n\n" \
                 f"user: Put on some music for me.\n3\n\n" \
                 f"user: I feel like hearing some music.\n3\n\n" \
                 f"user: Will you put on some relaxing music for me?\n3\n\n" \
                 f"user: Put some music on for me now.\n3\n\n" \
                 f"user: Play me some random music.\n3\n\n" \
                 f"user: Turn off my music\n4\n\n" \
                 f"user: Too much noise turn off my music\n4\n\n" \
                 f"user: Will you put on soothing music for me?\n5\n\n" \
                 f"user: I feel like relaxing, put on some music for me.\n5\n\n" \
                 f"user: Now it would fit some relaxing music\n5\n\n" \
                 f"user: Will you put on some upbeat muscia for me?\n6\n\n" \
                 f"user: I'm in the mood for a party would you put on some music for me?\n6\n\n" \
                 f"user: I'm in a party mood. Will you put some songs on me?\n6\n\n" \
                 f"user: I'm sad today\n9\n\nuser: I am very angry\n9\n\n" \
                 f"user: How are you? can't find my keys\n9\n\n" \
                 f"{transcribed_text}\n\n",

        response_emo = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=30,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        command = response_emo.choices[0].text.strip()
        print("detect_command: " + command)
        #print(prompt_text)
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
                moods = detect_emotions(message_text)
                response_text = natural_response(message_text)
                context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

                if command == '1':
                    ser.write(b'5')  # Invia il comando per spegnere la luce
                    execute_action(moods)
                    print("Light OFF")

                elif command == '2':
                    ser.write(b'6')  # Invia il comando per accendere la luce
                    execute_action(moods)
                    print("Light ON")

                elif command == '3':
                    ser.write(b'7')  # Invia il comando per spegnere la luce
                    execute_action(moods)
                    print("Music ON")

                elif command == '4':
                    ser.write(b'8')  # Invia il comando per accendere la luce
                    execute_action(moods)
                    print("Music OFF")

                elif command == '5':
                    ser.write(b'9')  # Invia il comando per spegnere la luce
                    execute_action(moods)
                    print("Relaxing music ON")

                elif command == '6':
                    ser.write(b'10')  # Invia il comando per accendere la luce
                    execute_action(moods)
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
def echo(update, context):
    message_text = update.message.text
    command = detect_command(message_text)
    moods = detect_emotions(message_text)
    response_text = natural_response(message_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

    if command == '1':
        ser.write(b'5')  # Invia il comando per spegnere la luce
        execute_action(moods)
        print("Light OFF")

    elif command == '2':
        ser.write(b'6')  # Invia il comando per accendere la luce
        execute_action(moods)
        print("Light ON")

    elif command == '3':
        ser.write(b'7')  # Invia il comando per spegnere la luce
        execute_action(moods)
        print("Music ON")

    elif command == '4':
        ser.write(b'8')  # Invia il comando per accendere la luce
        execute_action(moods)
        print("Music OFF")

    elif command == '5':
        ser.write(b'9')  # Invia il comando per spegnere la luce
        execute_action(moods)
        print("Relaxing music ON")

    elif command == '6':
        ser.write(b'10')  # Invia il comando per accendere la luce
        execute_action(moods)
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
        print("3 - anger")
    elif 'tranquility' in moods:
        ser.write(b'4')  # Invia il comando
        print("4 - tranquility")
    elif 'no mood' in moods:
        print("no mood")


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
