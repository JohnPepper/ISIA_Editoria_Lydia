def echo(update, context):
    message_text = update.message.text
    command = detect_command(message_text)
    moods = detect_emotions(message_text)
    response_text = natural_response(message_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

    if command == '1':
        ser.write(b'5')  # Invia il comando per spegnere la luce
        print("Light OFF")
