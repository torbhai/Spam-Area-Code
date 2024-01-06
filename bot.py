# Import the required libraries
import os
from telegram.ext import Updater
import telegram.ext
import pymongo
from pymongo import MongoClient
from asyncio import queues
from asyncio.queues import Queue


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
my_queue = queue.Queue()
updater = telegram.ext.Updater(bot, my_queue)


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
        context.bot.s