# Coded With Love From @TheLogman a indian coder
# Import the required libraries
import os
import telebot
import requests
import pandas as pd
import spacy
import googlemaps
import pyzipcode
# Load the NLP model
nlp = spacy.load("en_core_web_sm")

# Create a Google Maps client
gmaps = googlemaps.Client(key="AIzaSyCIOnwQY5_22u1NU_qjVXFGoV9hHQGOOJ8")

# Create a ZipCode database
db = pyzipcode.ZipCodeDatabase()

# Define a function that gets the city and state from an address
def get_city_state(address):
    # Use NLP to parse the address
    doc = nlp(address)
    # Initialize the city and state variables
    city = None
    state = None
    # Loop through the tokens in the address
    for token in doc:
        # If the token is a proper noun and the next token is a comma, assume it is the city name
        if token.pos_ == "PROPN" and token.nbor().text == ",":
            city = token.text
        # If the token is an uppercase word with length 2, assume it is the state code
        if token.is_upper and len(token) == 2:
            state = token.text
    # Return the city and state as a tuple
    return (city, state)

# Define a function that gets the coordinates from an address
def get_coordinates(address):
    # Use Google Maps geocoding to get the location data
    geocode_result = gmaps.geocode(address)
    # If the result is not empty, get the latitude and longitude
    if geocode_result:
        location = geocode_result[0]["geometry"]["location"]
        lat = location["lat"]
        lng = location["lng"]
        # Return the coordinates as a tuple
        return (lat, lng)
    # Otherwise, return None
    else:
        return None

# Define a function that gets the area codes from a postal code
def get_area_codes(postal_code):
    # Use pyzipcode to get the ZipCode object
    zip = db[postal_code]
    # Get the area codes as a list
    area_codes = zip.area_codes
    # Return the area codes
    return area_codes

# Define a function that finds the top 10 cities and their area codes for any bank
def find_top10_cities(bank_name):
    # Define the FDIC BankFind API URL
    api_url = "https://banks.data.fdic.gov/api/institutions"

    # Define the query parameters
    params = {
        "name": bank_name,
        "fields": "NAME,CITY,STALP,ADDRESS",
        "format": "json"
    }

    # Make a GET request to the API
    response = requests.get(api_url, params=params)

    # Check if the response is successful
    if response.status_code == 200:
        # Get the JSON data from the response
        data = response.json()
        # Get the list of banks from the data
        banks = data["data"]["institutions"]
        # Create an empty list to store the branch data
        branches = []
        # Loop through the banks
        for bank in banks:
            # Get the branch name, address, city, and state
            name = bank["NAME"]
            address = bank["ADDRESS"]
            city = bank["CITY"]
            state = bank["STALP"]
            # Get the city and state from the address using the get_city_state function
            city_state = get_city_state(address)
            # If the city and state are not None, use them instead of the ones from the API
            if city_state[0] and city_state[1]:
                city = city_state[0]
                state = city_state[1]
            # Get the coordinates from the address using the get_coordinates function
            coordinates = get_coordinates(address)
            # If the coordinates are not None, get the postal code from them using Google Maps reverse geocoding
            if coordinates:
                postal_code = gmaps.reverse_geocode(coordinates, result_type="postal_code")[0]["address_components"][0]["long_name"]
                # Get the area codes from the postal code using the get_area_codes function
                area_codes = get_area_codes(postal_code)
            # Otherwise, set the postal code and area codes to None
            else:
                postal_code = None
                area_codes = None
            # Create a dictionary with the branch data
            branch = {
                "name": name,
                "address": address,
                "city": city,
                "state": state,
                "coordinates": coordinates,
                "postal_code": postal_code,
                "area_codes": area_codes
            }
            # Append the branch data to the branches list
            branches.append(branch)
        # Create a pandas DataFrame from the branches list
        df = pd.DataFrame(branches)
        # Group the DataFrame by city and state and count the number of branches
        df_grouped = df.groupby(["city", "state"]).size().reset_index(name="count")
        # Sort the DataFrame by count in descending order
        df_sorted = df_grouped.sort_values(by="count", ascending=False)
        # Get the top 10 cities with the highest number of branches
        df_top10 = df_sorted.head(10)
        # Return the DataFrame
        return df_top10
    else:
        # Return None
        return None

# Define the bank name
bank_name = "Bank of America"

# Create a dictionary of banks and their area codes from the table
banks = {"Wells Fargo": [281, 346, 713, 832, 213, 310, 323, 424, 626, 818, 704, 980, 702, 725, 904, 415, 628, 305, 786, 404, 470, 678, 770, 215, 267, 445, 480, 602, 623, 928],
         "Chase": [212, 332, 347, 646, 718, 917, 929, 312, 630, 708, 773, 847, 872, 213, 310, 323, 424, 626, 818, 281, 346, 713, 832, 214, 469, 682, 817, 972, 210, 726, 480, 602, 623, 928, 619, 760, 858, 415, 628, 614, 380],
         "TD Bank": [212, 332, 347, 646, 718, 917, 929, 215, 267, 445, 617, 857, 305, 786, 202, 862, 973, 201, 551, 410, 443, 667, 754, 954],
         "Truist": [704, 980, 404, 470, 678, 770, 919, 984, 336, 321, 407, 813, 804, 305, 786, 904],
         "USAA": [210, 726, 719, 720, 480, 602, 623, 928, 813, 214, 469, 682, 817, 972, 410, 443, 667, 512, 737, 757, 948, 845],
         "NFCU": [571, 703, 619, 760, 858, 850, 904, 757, 948, 808, 202],
         "AFCU": [385, 801, 435, 656],
         "ENT": [719, 720, 303, 719],
         "Citi Bank": [212, 332, 347, 646, 718, 917, 929, 213, 310, 323, 424, 626, 818, 312, 630, 708, 773, 847, 872, 415, 628, 305, 786, 202, 617, 857, 619, 760, 858, 281, 346, 713, 832, 214, 469, 682, 817, 972]
         }

# Create a bot instance with our API Key
bot = telebot.TeleBot(6970286006:AAEOz3ky8GrSp0UfaRbIOv6ueVSM0KSr-Y4)

# Define a message handler that handles incoming text messages
@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Get the text message from the user
    bank_name = message.text
    # Check if the bank name is valid and in the dictionary
    if bank_name in banks:
        # Get the list of area codes for the bank
        area_codes = banks[bank_name]

