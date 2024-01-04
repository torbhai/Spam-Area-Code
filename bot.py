# Import the required libraries
import os
import telegram.ext
import telebot
from telegram.ext import Updater
from queue import Queue
from telegram import Bot

# The API Key we received for our bot
API_KEY = os.environ.get('BOT_TOKEN')

# Create a bot instance with our API Key
bot = telebot.TeleBot(API_KEY)

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
         "Wells": [505, 206, 702, 619, 408, 503, 559, 801, 323, 916, 253],
         "Chase": [313, 202, 646, 323, 347, 317, 408, 626, 254, 719, 732, 718, 856, 201],
         "AFCU": [385, 801, 435, 656],
         "ENT": [719, 720, 303, 719],
         "Citi Bank": [212, 332, 347, 646, 718, 917, 929, 213, 310, 323, 424, 626, 818, 312, 630, 708, 773, 847, 872, 415, 628, 305, 786, 202, 617, 857, 619, 760, 858, 281, 346, 713, 832, 214, 469, 682, 817, 972]
         }

# Define a function that handles the /start command
def start(update, context):
    # Send a welcome message to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, this is a bot that can tell you the area codes for different banks in the US. To use it, just type the bank name or select one of the buttons below.")
    # Create a reply keyboard markup with the buttons
    reply_keyboard = [["Wells", "Chase"], ["Manual Input", "Stop"]]
    reply_markup = telegram.ext.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    # Send the keyboard to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please choose an option:", reply_markup=reply_markup)

# Define a function that handles any text message
def text(update, context):
    # Get the text message from the user
    bank_name = update.message.text
    # Check if the bank name is valid and in the dictionary
    if bank_name in banks:
        # Get the list of area codes for the bank
        area_codes = banks[bank_name]
        # Sort the list in ascending order
        area_codes.sort()
        # Join the list elements with commas
        line = ", ".join(str(code) for code in area_codes)
        # Send the line to the user
        context.bot.send_message(chat_id=update.effective_chat.id, text="The area codes for " + bank_name + " are: " + line)
    elif bank_name == "Manual Input":
        # Send a message to the user to type a bank name
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please type a bank name.")
    elif bank_name == "Stop":
        # Call the stop function to stop the bot
        stop(update, context)
    elif bank_name == "":
        # Send an error message to the user if the message is empty
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please type a bank name or select a button.")
    else:
        # Send an error message to the user if the bank name is invalid
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid bank name. Please try again or select a button.")

# Define a function that handles the /stop command
def stop(update, context):
    # Send a goodbye message to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for using this bot. Goodbye.")
    # Remove the reply keyboard from the user
    reply_markup = telegram.ext.ReplyKeyboardRemove()
    context.bot.send_message(chat_id=update.effective_chat.id, text="The keyboard has been removed.", reply_markup=reply_markup)
    # Stop the bot from polling for updates
    updater.stop()

# Create a command handler for the /start command
start_handler = telegram.ext.CommandHandler('start', start)

# Create a command handler for the /stop command
stop_handler = telegram.ext.CommandHandler('stop', stop)

# Create a message handler for any text message
text_handler = telegram.ext.MessageHandler(telegram.ext.Filters.text, text)

# Add the handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(stop_handler)
dispatcher.add_handler(text_handler)

# Start polling for updates
updater.start_polling()
