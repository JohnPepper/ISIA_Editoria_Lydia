import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openai
import env

API_TOKEN = env.API_TOKEN
OPENAI_API_KEY = env.OPENAI_API_KEY

 #
openai.api_key = OPENAI_API_KEY
updater = Updater(token=API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def get_openai_response(message_text):
    prompt_text = f"It is the prompt aimed to control Smart home via telegram bot. \nReply to the user as a friend, in the same language the user is using.\n\nTo control their Smart Home the user can mention commands like:\n\n- \"Turn on the lights: warm/cold light, white/red/blue/yellow colour, intensity from 10% to 100%.\"\n- \"Turn on the music: calm, melancholic, happy, energetic, relaxing.\"\n\nDetect those commands, analyse user’s messages and detect emotions. If an emotion is detected, suggest corresponding settings for the Smart Home. If the user expresses feelings or state of being, respond accordingly and adjust the Smart Home settings for his comfort.\n\nThe format of the response should look like this, with detected emotions, commands and settings displayed first:\nUser: \"I'm a little tired today.\"\nBot: \"[Fatigue], (No command), [Light: Soft, warm/yellow, 50% intensity], [Music: Relaxing music]. Oh, I see. You're a little tired today. I set the lights to soft, warm/yellow, 50% intensity. I have also prepared relaxing music for you to help you relax and regenerate. Take care of yourself and try to rest when you can!\"\n\nDetected emotions and corresponding settings:\n\n[Happiness] Lights: Set lights to warm, orange, 100% intensity.\n[Happiness] Music: Play a happy song.\n\n[Sadness] Lights: Set lights to soft, cool/blue, 50% intensity.\n[Sadness] Music: Play a melancholic song.\n\n[Anger] Lights: Set lights to intense, red/violet, 100% intensity.\n[Anger] Music: Play an energetic song.\n\n[Fear] Lights: Set lights to soft, warm/white, 50% intensity.\n[Fear] Music: Play calming music.\n\n[Calmness] Lights: Set lights to neutral/white/blue, 70% intensity.\n[Calmness] Music: Play calming music.\n\n[Fatigue] Lights: Set lights to soft, warm/yellow, 50% intensity.\n[Fatigue] Music: Play relaxing music.\n{message_text}?",

    #prompt_text = f"Dato un messaggio come input, Voglio che tu mi risponda in maniera naturale e tra parentesi quadrate mi metti lo stato d'animo dell'input\n\nGli stati d'animo devo essere scelti tra i seguenti:\nFelicità\nTristezza\nPaura\nRabbia\nCalma\n{message_text}?"
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


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, echo))

updater.start_polling()