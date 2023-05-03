import telebot
import openai

API_TOKEN = '5627308480:AAH0kfXZSvVdI1fb24Jc5v3v5Cec6rpaN98'
OPENAI_API_KEY = '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'


# Inizializza bot telegram
bot = telebot.TeleBot(API_TOKEN)

# Inizializza l'API di OpenAI
openai.api_key = OPENAI_API_KEY


# Funzione per ottenere la risposta dal modello di OpenAI
def get_openai_response(message_text):

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"rispondimi in maniera naturale ai messaggi come se fossi un amico {message_text}?",
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\"\"\""]
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
    # Ottengo la risposta dal modello di OpenAI
    response = get_openai_response(message.text)
    bot.reply_to(message, response)


bot.polling()


