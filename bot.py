# Import the required libraries
import os
from telegram.ext import Updater
from queue import Queue
import telegram.ext
import pymongo
from pymongo import MongoClient
import requests
import bitcoinlib


# Replace the connection string with your own
connection_string = "mongodb://mongo:6bHFBAd2fEg5d-ce-aeEGfAAG5b5a2Hb@viaduct.proxy.rlwy.net:45701"

# Create a MongoClient object
client = MongoClient(connection_string)

# Access the database
db = client.test

# Access the collection
collection = db["new collection"]

# Create a document
test = {"chat_id": "6950394833",
        "user_name": "TheLogman",
        "status": "premium"}

# Insert the document into the collection
collection.insert_one(test)


# The API Key we received for our bot
API_KEY = os.environ.get('BOT_TOKEN')

# use the default value of None
updater = telegram.ext.Updater(API_KEY)

# Retrieve the dispatcher, which will be used to add handlers
dispatcher = updater.dispatcher

# Create a dictionary of banks and their area codes from the table
banks = {"Wells Fargo": [281, 346, 713, 832, 213, 310, 323, 424, 626, 818, 704, 980, 702, 725, 904, 415, 628, 305, 786, 404, 470, 678, 770, 215, 267, 445, 480, 602, 623, 928],
         "Chase": [212, 332, 347, 646, 718, 917, 929, 312, 630, 708, 773, 847, 872, 213, 310, 323, 424, 626, 818, 281, 346, 713, 832, 214, 469, 682, 817, 972, 210, 726, 480, 602, 623, 928, 619, 760, 858, 415, 628, 614, 380],
         "TD Bank": [212, 332, 347, 646, 718, 917, 929, 215, 267, 445, 617, 857, 305, 786, 202, 862, 973, 201, 551, 410, 443, 667, 754, 954],
         "Truist": [704, 980, 404, 470, 678, 770, 919, 984, 336, 321, 407, 813, 804, 305, 786, 904],
         "USAA": [210, 726, 719, 720, 480, 602, 623, 928, 813, 214, 469, 682, 817, 972, 410, 443, 667, 512, 737, 757, 948, 845],
         "NFCU": [571, 703, 619, 760, 858, 850, 904, 757, 948, 808, 202],
         "wells": [505, 206, 702, 619, 408, 503, 559, 801, 323, 916, 253],
         "chase": [313, 202, 646, 323, 347, 317, 408, 626, 254, 719, 732, 718, 856, 201],
         "AFCU": [385, 801, 435, 656],
         "ENT": [719, 720, 303, 719],
         "Citi Bank": [212, 332, 347, 646, 718, 917, 929, 213, 310, 323, 424, 626, 818, 312, 630, 708, 773, 847, 872, 415, 628, 305, 786, 202, 617, 857, 619, 760, 858, 281, 346, 713, 832, 214, 469, 682, 817, 972]
         }

# Define a function that handles the /start command
def start(update, context):
    # Send a welcome message to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, this is a bot that can tell you the area codes for different banks in the US. To use it, just type the bank name. Created by @TheLogman")

# Define a function that handles any text message
# Define a function that handles any text message
def text(update, context):
    # Get the text message from the user
    bank_name = update.message.text
    # Get the chat id of the user
    chat_id = update.message.chat.id
    # Query the collection to find the document that matches the chat id
    user = collection.find_one({"chat_id": chat_id})
    # Check if the user is a premium user or not
    if user and user.get("status") == "premium":
        # The user is a premium user, execute the existing code
        # Check if the bank name is valid and in the dictionary
        if bank_name in banks:
            # Get the list of area codes for the bank
            area_codes = banks[bank_name]
            # Join the list elements with commas
            line = ", ".join(str(code) for code in area_codes)
            # Send the line to the user
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"The area codes for {bank_name} are: {line}")
        else:
            # Send an error message to the user
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid bank name. Please try again.")
    else:
        # The user is not a premium user, send a message to the user informing them that they need to subscribe to use the bot
        context.bot.send_message(chat_id=update.effective_chat.id, text="You need to subscribe to use this bot. Please use the /subscribe command to start the payment process.")
# Define a function that handles the /subscribe command
def subscribe(update, context):
    # Get the chat id and the username of the user
    chat_id = update.message.chat.id
    user_name = update.message.chat.username
    # Get the Bitcoin address and the amount in BTC
    btc_address = "1Gu7Nqy7LDSFo4dFLbSCmZ6XjCAV55sLNf"
    # Make a GET request to the Bitcoin API
    response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")

    # Parse the response as a JSON object
    data = response.json()

    # Get the exchange rate of BTC and USD as a float
    btc_rate = data["bpi"]["USD"]["rate_float"]

    # Get the USD amount from the user input and convert it to a float
    usd_amount = float(25)

    # Calculate the BTC amount by dividing the USD amount by the exchange rate
    btc_amount = usd_amount / btc_rate

    # Send a message to the user with the address and the amount
    context.bot.send_message(chat_id, text=f"Please send {btc_amount} BTC ({usd_amount} USD) to this address: {btc_address}")
    # Create a keyboard with two buttons: "Paid" and "Cancel"
    keyboard = telegram.InlineKeyboardMarkup([
        [telegram.InlineKeyboardButton("Paid", callback_data=f"{chat_id}-{user_name}-paid"),
         telegram.InlineKeyboardButton("Cancel", callback_data=f"{chat_id}-{user_name}-cancel")]
    ])
    # Send the keyboard to the user
    context.bot.send_message(chat_id, text="Please select an option:", reply_markup=keyboard)

    # Define a function that handles the button clicks
    def button(update, context):
         # Get the callback query
         query = update.callback_query
         # Acknowledge the callback query
         query.answer()
         # Get the chat id, the username, and the option from the callback data
         chat_id, user_name, option = query.data.split("-")
         # Check the option
         if option == "paid":
        # The user clicked the "Paid" button
        # Ask the user for the transaction hash
             context.bot.send_message(chat_id, text="Please enter the transaction hash of your payment:")
        # Define a function that handles the transaction hash
             def tx_hash(update, context):
            # Get the transaction hash from the user
                 tx_hash = update.message.text
            # Create a key object from the address
                 key = bitcoinlib.keys.Key(address=address.address)
            # Create a transaction object from the transaction hash
                 tx = bitcoinlib.transactions.Transaction.import_raw(tx_hash, network="bitcoin")
            # Get the number of confirmations and the amount of the transaction
                 confirmations = tx.confirmations()
                 amount = tx.output_total(key)
            # Check if the transaction is valid
                 if confirmations > 0 and amount >= btc_amount:
                # The transaction is valid
                # Check if the transaction has at least 2 confirmations
                     if confirmations >= 2:
                    # The transaction has enough confirmations
                    # Get the current date and the expiration date
                         current_date = datetime.date.today()
                         expiration_date = current_date + datetime.timedelta(days=30)
                    # Update the MongoDB database with the user's subscription status and expiration date
                         collection.update_one({"chat_id": chat_id}, {"$set": {"status": "premium", "expiration_date": expiration_date}})
                    # Send a confirmation message to the user
                         context.bot.send_message(chat_id, text=f"Thank you for your payment, {user_name}! You are now a premium user until {expiration_date}. Enjoy the bot!")
                else:
                    # The transaction does not have enough confirmations
                    # Send a message to the user informing them that they need to wait for more confirmations
                    context.bot.send_message(chat_id, text=f"Your payment is pending confirmation. Please wait until it has at least 2 confirmations. You can check the status of your transaction [here](https://stackoverflow.com/questions/67930142/how-can-i-add-custom-command-using-python-telegram-bot).")
        else:
                # The transaction is invalid
                # Send an error message to the user
        context.bot.send_message(chat_id, text="Invalid transaction. Please make sure you have sent the correct amount to the correct address and that your transaction has at least 1 confirmation.")
        # Create a message handler for the transaction hash
        tx_hash_handler = telegram.ext.MessageHandler(telegram.ext.Filters.text, tx_hash)
        # Add the handler to the dispatcher
        dispatcher.add_handler(tx_hash_handler)
    elif option == "cancel":
        # The user clicked the "Cancel" button
        # Edit the message that contains the keyboard
        query.edit_message_text(text="You have canceled the payment process. You can use the /subscribe command again if you change your mind.")
    else:
        # The user clicked an unknown button
        # Send an error message to the user
        context.bot.send_message(chat_id, text="Unknown option. Please try again.")

# Create a handler for the button clicks
button_handler = telegram.ext.CallbackQueryHandler(button)
# Add the handler to the dispatcher
dispatcher.add_handler(button_handler)

# Create a command handler for the /start command
start_handler = telegram.ext.CommandHandler('start', start)

# Create a message handler for any text message
text_handler = telegram.ext.MessageHandler(telegram.ext.Filters.text, text)

# Add the handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(text_handler)

# Start polling for updates
updater.start_polling()
