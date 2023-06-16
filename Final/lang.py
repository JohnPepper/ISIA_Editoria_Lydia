# https://stackoverflow.com/questions/21271733/multi-language-support-in-python-script

MSG_EMOTION_HAPPINESS = 1
MSG_EMOTION_SAD = 2
MSG_EMOTION_FEAR = 3
MSG_EMOTION_ANGER = 4
MSG_EMOTION_CALM = 5
MSG_PROMPT = 101

msg_en = {
    MSG_EMOTION_HAPPINESS: 'happiness',
    MSG_EMOTION_SAD: 'sadness',
    MSG_EMOTION_FEAR: 'fear',
    MSG_EMOTION_ANGER: 'anger',
    MSG_EMOTION_CALM: 'calm',
    MSG_PROMPT: "Given a message as input, I want you to respond to me naturally and put the mood of the input in square brackets \n\nThe moods should be chosen from the following:\nhappiness\nsad\nfear\nanger\ncalm\n",
}

msg_it = {
    MSG_EMOTION_HAPPINESS: 'felicità',
    MSG_EMOTION_SAD: 'trsitezza',
    MSG_EMOTION_FEAR: 'paura',
    MSG_EMOTION_ANGER: 'rabbia',
    MSG_EMOTION_CALM: 'calma',
    MSG_PROMPT: "Dato un messaggio come input, Voglio che tu mi risponda in maniera naturale e tra parentesi quadrate mi metti lo stato d'animo dell'input\n\nGli stati d'animo devo essere scelti tra i seguenti:\nFelicità\nTristezza\nPaura\nRabbia\nCalma\n",
}

msg = msg_en

print(msg[MSG_PROMPT])
