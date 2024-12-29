# This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager
# classes to achieve the program requirements.

import os
import pandas
import csv
from data_manager import DataManager
from flight_search import FlightSearch
from flight_location_search import LocationSearch
import pprint
import datetime
from dateutil.relativedelta import relativedelta
from flight_data import FlightData
import json

import ollama
from openai import OpenAI


# create a file path to pass to the destination object.
file_path = os.path.join(".", "FlightData", "FlightDeals.csv")

# Create a destinations object
destinations = DataManager(file_path=file_path)

# load the list of destinations dictionaries
dest_list = destinations.destination_list

# print(dest_list)

# Get today's date as the from date in dd/mm/YYYY format
today = datetime.datetime.now()

# Get the date six months from today date calculated above fpr the date to as dd/mm/YYYY format
six_month = today + relativedelta(months=+6)

# Conver the dates to strings in FlightSearch required format
today = today.strftime("%d/%m/%Y")
six_month = six_month.strftime("%d/%m/%Y")


fly_location = "Georgia"
get_city = LocationSearch(fly_location).data
print(len(get_city["locations"]))

fly_location_airports = []

for location in get_city["locations"]:
    fly_location_airports.append(
        {"IATA Code": location["code"], "City": location["name"]}
    )

print(fly_location_airports)


def user_prompt_for(location: str, airport_list: list):
    system_prompt = """ Your an experienced and helpful travel agent with knowledge on cities around the world and best airport to travel to 
                        when a user is looking to fly to a city, state, country or region. You will be provided a list of airports in a list of dictionaries format. 
                        You will parse this list and respond back with the City Name and airport IATA code the user should use when booking a flight to said location,
                        based on the popularity of the airport and distance to and from the airport to the city or country capital if the city is not provided. 
                        You will be provided a list of airpots as the following example for New York.
                    """
    airports = """[
                        {'IATA Code': 'JFK', 'City': 'John F. Kennedy International'}, 
                        {'IATA Code': 'EWR', 'City': 'Newark Liberty International'}, 
                        {'IATA Code': 'LGA', 'City': 'LaGuardia'}, 
                        {'IATA Code': 'SWF', 'City': 'New York Stewart International Airport'}
                                    
                    ]"""

    system_prompt += airports
    system_prompt += """You will respond with a JSON object with the following format. Just output the raw json object, do not prefix it with ```json.:
                        {
                            "City": "New York",
                            "IATA Code": "JFK"
                        }

                        There may be instances when the user does not provide a city and rather provides a state or regional area. For example, they might provide a location
                        like Florida. In this case there are a few options like Orlando or Miami. You will choose one based on popularity and closeness to turist attractions.
                        """
    print(system_prompt)
    user_prompt = f""" I'd like to travel to {location}, but I'm unsure about what airport to travel to. 
                       Can you help me get the best airport from the following choices: {airport_list}?
                   """
    print(user_prompt)

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return message


def call_ai_for_airport(llm):
    if llm.lower() == "openai":
        api_key = os.getenv("OPEN_AI_API_TOKEN")
        openai = OpenAI(api_key=api_key)

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=user_prompt_for(
                location=fly_location, airport_list=fly_location_airports
            ),
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
    else:

        response = ollama.chat(
            model="llama3.2",
            messages=user_prompt_for(
                location=fly_location, airport_list=fly_location_airports
            ),
            format="json",
        )

        return response["message"]["content"]


results = json.loads(call_ai_for_airport(llm="llama"))

print(results)
# print(type(results))
# print(results["IATA Code"])


flight_search = FlightSearch(
    fly_from="NYC", fly_to=results["IATA Code"], date_from=today, date_to=six_month
)

print(flight_search.data)

flight_results = FlightData(flight_results=flight_search.data, desired_price=3000)

# print(flight_results)

# print(airports)

# Iterate through the destination list and grab flights
# Also pass the results to check if we find a flight with a lower price than desired price.
# for item in dest_list:
#     to = item["IATA Code"]
#     city = item["City"]
#     max_price = item["Lowest Price"]
#     # Create a flight search object
#     flight_search = FlightSearch(
#         fly_from="NYC", fly_to=to, date_from=today, date_to=six_month
#     )

#     flight_results = FlightData(
#         flight_results=flight_search.data, desired_price=max_price
#     )
