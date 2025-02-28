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


fly_location = "Florida"
get_city = LocationSearch(fly_location).data
# print(len(get_city["locations"]))

fly_location_airports = []

for location in get_city["locations"]:
    fly_location_airports.append(
        {"IATA Code": location["code"], "City": location["name"]}
    )

# print(fly_location_airports)

###################################################
#                    FUNCTIONS                    #
###################################################

# Flight Search Function


def flight_search(fly_from: str, fly_to: str, date_from: str, date_to: str):
    # Create a flight search object
    fly_search_results = FlightSearch(
        fly_from=fly_from,
        fly_to=fly_to,
        date_from=date_from,
        date_to=date_to,
    )

    # Get the flight data
    # print(fly_search_results.data)
    fly_data = fly_search_results.data

    # Create a flight data object
    flight_data = FlightData(fly_data).flight_data
    # print(flight_data)

    return fly_data


flight_search_function = {
    "name": "flight_search",
    "description": "Get the price of a return ticket to the destination city. Call this whenever you need to know the ticket price, for example when a customer asks 'How much is a ticket to this city'",
    "parameters": {
        "type": "object",
        "properties": {
            "fly_from": {
                "type": "string",
                "description": "The city that the customer wants to travel from. If the customer provides a city name you need to convert to airport code. For example Orlando is MCO.",
            },
            "fly_to": {
                "type": "string",
                "description": "The city that the customer wants to travel to. If the customer provides a city name you need to convert to airport code. For example Orlando is MCO.",
            },
            "date_from": {
                "type": "string",
                "description": "The start date the customer wants to depart. The function expects the format as 'dd/mm/YYYY'.",
            },
            "date_to": {
                "type": "string",
                "description": "The start date the customer wants to return. The function expects the format as 'dd/mm/YYYY'.",
            },
        },
        "required": ["fly_from", "fly_to", "date_from", "date_to"],
        "additionalProperties": False,
    },
}

tools = [
    {
        "type": "function",
        "function": flight_search_function,
    }
]


def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    fly_from = arguments.get("fly_from")
    fly_to = arguments.get("fly_to")
    date_from = arguments.get("date_from")
    date_to = arguments.get("date_to")
    flight_info = flight_search(fly_from, fly_to, date_from, date_to)
    response = {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(flight_info),
    }
    return response


###################################################
#                    FUNCTIONS                    #
###################################################


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
    # print(system_prompt)
    user_prompt = f""" I'd like to travel to {location}, but I'm unsure about what airport to travel to. 
                       Can you help me get the best airport from the following choices: {airport_list}?
                   """
    # print(user_prompt)

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return message


def call_chat_ai(mesasge, history):

    system_message = f""" You are a helpful and enthusiastic assistant for an airline travel agency called FlightAI. Give short, courteous answers, no more than 1 sentence. Always be accurate.
                     At the start of the conversation always introduce yourself. Tell the customer to type exit to end the conversation once they are done.
                     If you don't know or have accurate information to answer, say so. Don't make up an answer. Do not answer questions that are not related to your job as a travel agent for FlightAI.
                     You just say that's outside your scope. Today's date is {datetime.datetime.now().strftime("%d-%m-%Y")}.
                     The date is provided and needs to keep the dd/mm/YYYY (Day-Month-Year) format, keep that in mind when manipulating dates.
                     For example, if user says tomorrow and today's date is 11/01/2024, then tomorrow's date is 12/01/2024.
                     Provide information to the user such as the airline, travel duration, flight cost and depart times.
                     Expand the airline codes to a user friendly name, for example "NK" is Spirit Airlines and "AA" is American AIrlines.
                 """
    messages = [
        {"role": "system", "content": system_message},
    ]

    for user_message, assistant_message in history:
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": assistant_message})
    messages.append({"role": "user", "content": mesasge})

    # response = ollama.chat(
    #     model="llama3.2",
    #     messages=messages,
    #     tools=tools,
    #     stream=False,
    # )
    # print(response["message"]["content"])
    # return response["message"]["content"]
    api_key = os.getenv("OPEN_AI_API_TOKEN")
    openai = OpenAI(api_key=api_key)

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
    )
    if response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        messages.append(
            {
                "role": "assistant",
                "content": message.content if message.content else "",
                "tool_calls": message.tool_calls,
            }
        )
        # flight_info = handle_tool_call(message)
        # print(flight_info)
        # # messages.append(message)
        # messages.append(flight_info)
        # Handle each tool call individually
        for tool_call in message.tool_calls:
            flight_info = handle_tool_call(message)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": json.dumps(flight_info),
                }
            )
        # print(messages)
        response = openai.chat.completions.create(
            model="gpt-4o-mini", messages=messages
        )

    return response.choices[0].message.content
    # return response.choices[0].message.content


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


def chat():
    history = []
    print(
        """Welcome to FlightAI. Your one-stop destination to book great vacations!\nFeel free to ask our AI questions about different flight options to great destinations.\n"""
    )

    while True:
        user_message = input("User: ")
        print("\n")
        if user_message.lower() == "exit":
            break
        assistant_message = call_chat_ai(user_message, history)
        print(f"Assistant: {assistant_message}")
        print("\n")
        history.append((user_message, assistant_message))


chat()


# results = json.loads(call_ai_for_airport(llm="llama"))

# print(results)
# # print(type(results))
# # print(results["IATA Code"])


# flight_search = FlightSearch(
#     fly_from="NYC", fly_to=results["IATA Code"], date_from=today, date_to=six_month
# )

# print(flight_search.data)

# flight_results = FlightData(flight_results=flight_search.data, desired_price=3000)

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
