import requests

ENDPOINT = "http://127.0.0.1:5001"
username = "User"
botname = "Assistant"
conversation_history = ""

def generate_response(prompt):
    payload = {
        "prompt": prompt,
        "max_length": 120,
        "temperature": 0.6
    }
    response = requests.post(f"{ENDPOINT}/api/v1/generate", json=payload)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0].get("text", "").strip()
    return "Error: No valid response from API."

while True:
    user_input = input(f"{username}: ")
    # Append user input to the conversation history
    conversation_history += f"{username}: {user_input}\n"
    # Construct the prompt by appending the bot name
    prompt = conversation_history + f"{botname}:"
    # Generate and print the bot's response
    bot_response = generate_response(prompt)
    print(f"{botname}: {bot_response}")
    # Update conversation history with bot's response
    conversation_history += f"{botname}: {bot_response}\n"
