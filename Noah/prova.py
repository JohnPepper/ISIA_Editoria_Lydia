import openai
openai.api_key = "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"

def riconosci_stato_danimo(frase):
    modello = "text-davinci-002"
    prompt = (f"Lo stato d'animo di questa frase è: ")
    completamento = openai.Completion.create(
        engine=modello,
        prompt=prompt,
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.7,
        frequency_penalty=0,
        presence_penalty=0
    )
    risposta = completamento.choices[0].text.strip()
    return risposta

frase = input("Inserisci la frase da analizzare: ")
stato_danimo = riconosci_stato_danimo(frase)
print(stato_danimo)