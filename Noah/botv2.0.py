import telebot
import openai

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

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Valuta da una scala da uno a 10 quanto è depressa la frase:\n\nQ: Oggi è un bruttissima giornata\nA: 8\nQ: Uffa\nA: 6\nQ: Oggi è un ho litigato con il capo \nA: 7\nQ: Mi ha lasciatpo la ragazza, sono depresso\nA: 9 {message_text}?",
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
    # Controlla se "accendi led" è presente nel testo del messaggio
    if "accendi led" in message.text:
        ser.write(b'1') # inviare il carattere '1' alla seriale
        # Ottiene la risposta dal modello di OpenAI basata sul testo del messaggio
        response = get_openai_response(message.text)
        bot.reply_to(message, response)
    else:
        # Ottengo la risposta dal modello di OpenAI
        response = get_openai_response(message.text)
        bot.reply_to(message, response)

bot.polling()





