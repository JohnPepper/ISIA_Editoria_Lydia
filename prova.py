import os
import openai

openai.api_key = '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'

start_sequence = "\nA:"
restart_sequence = "\n\nQ: "

response = openai.Completion.create(
  model="text-davinci-003",
  prompt="Valuta da una scala da uno a 10 quanto è depressa la frase:\n\nQ: Oggi è un bruttissima giornata\nA: 8\nQ: Uffa\nA: 6\nQ: Oggi è un ho litigato con il capo \nA: 7\nQ: Mi ha lasciatpo la ragazza, sono depresso\nA: 9",
  temperature=0,
  max_tokens=100,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0,
  stop=["\n"]
)

generated_text = response.choices[0].text.strip()
print(generated_text)
