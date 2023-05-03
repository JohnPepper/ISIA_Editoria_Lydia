import telebot
import openai
import re
import serial
import time

API_TOKEN = '5627308480:AAH0kfXZSvVdI1fb24Jc5v3v5Cec6rpaN98' #telegram token, no change
OPENAI_API_KEY = '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' #OpenAI token, to change
ser = serial.Serial('/dev/cu.SLAB_USBtoUART', 115200)


# Inizializza bot telegram
bot = telebot.TeleBot(API_TOKEN)

# Inizializza l'API di OpenAI
openai.api_key = OPENAI_API_KEY


# Funzione per ottenere la risposta dal modello di OpenAI
def get_openai_response(message_text):
    prompt_text = f"Dato un messaggio come input, Voglio che tu mi risponda in maniera naturale e tra parentesi quadrate mi metti lo stato d'animo dell'input\n\nGli stati d'animo devo essere scelti tra i seguenti:\nFelicità\nTristezza\nPaura\nRabbia\nCalma\n{message_text}?"
    prompt_text = re.sub(r'\[.*?\]', '', prompt_text) #rimuove le parole tra parentesi quadre
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



# Gestisce '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
    Benvenuto nel primo BOT di prova
    """)

# Gestisce tutti gli altri messaggi con content_type 'text' (content_types è predefinito a ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    response = get_openai_response(message.text) #risposta dal modello di OpenAI
    moods = re.findall(r'\[(.*?)\]', response)#La parola tra parentesi quadre la salva in una variabile
    # Rimuove le parole tra parentesi quadre dalla risposta
    response = re.sub(r'\[.*?\]', '', response)
    execute_action(moods) # Invia il comando all'ESP32 in base allo stato d'animo
    bot.reply_to(message, response)
    # Stampa lo stato d'animo nel terminale
    print(f"Stato d'animo: {moods}")


def execute_action(moods):
    if 'felicità' in moods:
        ser.write(b'LED_ON\n') # Invia il comando per accendere il LED
    elif 'tristezza' in moods:
        ser.write(b'LED_OFF\n') # Invia il comando per spegnere il LED
    elif 'paura' in moods:
        ser.write(b'LED_OFF\n') # Invia il comando per accendere il buzzer
    elif 'rabbia' in moods:
        ser.write(b'LED_OFF\n') # Invia il comando per spegnere il buzzer
    elif 'calma' in moods:
        ser.write(b'LED_ON\n')  # Invia il comando per spegnere il buzzer

bot.polling()

