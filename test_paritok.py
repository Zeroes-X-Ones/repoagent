from openai import OpenAI

client = OpenAI(
    api_key="dummy",
    base_url="http://127.0.0.1:8080/v1"
)

response = client.chat.completions.create(
    model="anthropic/claude-3.7-sonnet",
    messages=[
        {"role": "user", "content": "Say hello"}
    ]
)

print(response)