from openai import OpenAI
import json
with open('GPT_TOKEN.json') as file_:
    data_ = json.load(file_)

api_key = data_['key']



client = OpenAI(
    api_key=api_key,
    base_url="https://zukijourney.xyzbot.net/v1" # or "https://zukijourney.xyzbot.net/unf"
)

chat_completion = client.chat.completions.create(
    stream=False, # can be true
    model="mistral-medium",  # "gpt-4",
    messages=[
        {
            "role": "user",
            "content": 'There are 50 books in a library. Sam decides to read 5 of the books. How many books are there now? If there are 45 books, say "1". Else, if there is the same amount of books, say "2".', #responds 2: gpt-4, responds 1: gpt-3.5
        },
    ],
)
print(chat_completion)