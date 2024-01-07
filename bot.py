import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, filters

# Replace with your own API key and base URL from https://goo.by/telegram-url-shortener-bot
API_KEY = "3f423f33015e1a8f6bb7"
BASE_URL = "https://goo.by/shorten"

# Replace with your own IP address for the custom domain
IP_ADDRESS = "your-ip-address-here"

# Create a bot instance
bot = telegram.Bot(token=BOT_TOKEN)

# Create an updater instance
updater = Updater(token=BOT_TOKEN, use_context=True)

# Define a function to handle the /start command
def start(update, context):
    # Send a welcome message
    update.message.reply_text("Hello, I am a URL shortener bot. I can help you create short URLs with a custom domain. To get started, please send me your custom domain name.")

# Define a function to handle the /help command
def help(update, context):
    # Send a help message
    update.message.reply_text("Here are the steps to use this bot:\n1. Send me your custom domain name.\n2. I will give you an IP address to update on your DNS record.\n3. Send me the main URL that you want to shorten.\n4. I will send you the shortened URL with your custom domain.")

# Define a function to handle text messages
def text(update, context):
    # Get the text message from the user
    text = update.message.text

    # Check if the text is a valid domain name
    if text.endswith(".com") or text.endswith(".net") or text.endswith(".org"):
        # Store the domain name in the user data
        context.user_data["domain"] = text
        # Send the IP address to update on the DNS record
        update.message.reply_text(f"OK, your custom domain name is {text}. Please update your DNS record with this IP address: {IP_ADDRESS}. Then send me the main URL that you want to shorten.")
    # Check if the text is a valid URL
    elif text.startswith("http://") or text.startswith("https://"):
        # Get the domain name from the user data
        domain = context.user_data.get("domain")
        # Check if the domain name is set
        if domain:
            # Shorten the URL using the API
            payload = {"long_url": text, "api_key": API_KEY, "domain": domain}
            response = requests.post(BASE_URL, data=payload)
            # Check if the response is successful
            if response.status_code == 200:
                # Get the shortened URL from the response
                short_url = response.text
                # Send the shortened URL to the user
                update.message.reply_text(f"Here is your shortened URL: {short_url}")
            else:
                # Send an error message
                update.message.reply_text(f"Sorry, something went wrong. Please try again later.")
        else:
            # Send a reminder message
            update.message.reply_text("Please send me your custom domain name first.")
    else:
        # Send an invalid message
        update.message.reply_text("Please send me a valid domain name or URL.")
        
# Add handlers to the dispatcher
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help))
dispatcher.add_handler(MessageHandler(Filters.text, text))

# Start the bot
updater.start_polling()
updater.idle()
