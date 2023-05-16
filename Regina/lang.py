# https://stackoverflow.com/questions/21271733/multi-language-support-in-python-script

MSG_EMOTION_ANGER = 1
MSG_EMOTION_HAPPINESS = 2
MSG_WELCOME = 100
MSG_PROMPT = 101

msg_en = {
    MSG_EMOTION_ANGER: 'anger',
    MSG_EMOTION_HAPPINESS: 'happiness',
    MSG_WELCOME: 'welcome to this bot ...',
    MSG_PROMPT: 'analyze this text ....',
}

msg_it = {
    MSG_EMOTION_ANGER: 'rabbia',
    MSG_EMOTION_HAPPINESS: 'felicità',
    MSG_WELCOME: 'benvenuto al bot ...',
    MSG_PROMPT: 'analizza questo testo ....',
}

msg = msg_en

print(msg[MSG_WELCOME])
