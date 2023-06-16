def voice_handler(update, context):
    message = update.message
    if message.voice:
        # Get file path on Telegram server
        voice_file = message.voice
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
            #save the downloaded audio file
            with open(file_path, 'wb') as f:
                f.write(response.content)
                print("SAVED VOICE MESSAGE - as ogg")
                # Send a confirmation message
                context.bot.send_message(chat_id=update.effective_chat.id, text="Voice message saved.")
                try:
                    #Try process emotion then send to chat.
                    emotion = process_voice_messages(file_path)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{emotion}")
                except Exception as e:
                    print("Error:", e)
        except Exception as e:
            print("Error:", e)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Error occurred while saving the voice message.")
    elif message.text:
        # Process text message as a command to turn on or off the light
        command = re.findall(r'(accendi|spegni) (la )?(luce)', message.text, flags=re.IGNORECASE)
        if command:
            if command[0][0].lower() == "accendi":
                ser.write(b'6')
                context.bot.send_message(chat_id=update.effective_chat.id, text="Luce accesa!")
            elif command[0][0].lower() == "spegni":
                ser.write(b'7')
                context.bot.send_message(chat_id=update.effective_chat.id, text="Luce spenta!")
        else:
            # If no command is recognized, process the message for emotion
            try:
                emotion = process_voice_messages(message.text)
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"{emotion}")
            except Exception as e:
                print("Error:", e)
                context.bot.send_message(chat_id=update.effective_chat.id, text="Error occurred while processing the message for emotion.")

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
        #save the downloaded audio file
        with open(file_path, 'wb') as f:
            f.write(response.content)
            print("SAVED VOICE MESSAGE - as ogg")
            # Send a confirmation message
            context.bot.send_message(chat_id=update.effective_chat.id, text="Voice message saved.")
            try:
                #Try process emotion then send to chat.
                emotion = process_voice_messages(file_path)
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"{emotion}")
            except Exception as e:
                print("Error:", e)
    except Exception as e:
        print("Error:", e)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Error occurred while saving the voice message.")
