import telebot
import requests
import random

bot_token = "6970286006:AAEOz3ky8GrSp0UfaRbIOv6ueVSM0KSr-Y4"
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Spamicode Bank Number Leads Bot Created by @TheLogman! Please enter the name of the bank and the desired number of leads.")

@bot.message_handler(func=lambda message: True)
def generate_number_leads(message):
    user_input = message.text.split()
    bank_name = user_input[0]
    num_leads = int(user_input[1])

    # Use ChatGPT to find the top 10 cities of the bank with area codes

    # Make a request to the ChatGPT model
    response = requests.post(
        "https://api.openai.com/v1/engines/davinci-codex/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer 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"
        },
        json={
            "prompt": f"List of top 10 cities of {bank_name} with area codes in United States based on highest number of branches:",
            "max_tokens": 100,
            "temperature": 0.6
        }
    )

    # Parse the response and extract the generated cities with area codes
    generated_text = response.json()["choices"][0]["text"]
    cities_with_area_codes = generated_text.split("\n")

    # Generate the number leads
    number_leads = []
    for i in range(num_leads):
        city_with_area_code = random.choice(cities_with_area_codes)
        area_code = city_with_area_code.split(":")[1].strip()
        country_code = "+1"  # USA country code
        last_seven_digits = str(random.randint(1000000, 9999999))
        number = country_code + area_code + last_seven_digits
        number_leads.append(number)

    # Save the number leads to a text file
    with open("number_leads.txt", "w") as file:
        file.write("\n".join(number_leads))

    # Send the number leads file to the user
    with open("number_leads.txt", "rb") as file:
        bot.send_document(message.chat.id, file)

bot.polling()
