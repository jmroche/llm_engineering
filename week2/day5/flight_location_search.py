import requests
import os


class LocationSearch:
    # This class is responsible for talking to the Flight Location API.
    # The correct date format is dd/mm/YYYY, e.g. 29/05/2021
    """Flight Location Search class. Gets parameters from object to structure,
    the API query parameters and initialize the object. After,
    calls the api_call function to request data passsed at object
    initialization.
    """

    def __init__(self, fly_location):
        self.kiwi_api_url = "https://api.tequila.kiwi.com/locations/query"
        self.kiwi_apikey = os.getenv("KIWI_API_TOKEN")
        self.fly_location = fly_location

        self.kiwi_api_parameters = {
            "term": self.fly_location,
            "locale": "en-US",
            "location_types": "airport",
            "limit": 10,
            "active_only": True,
        }

        self.kiwi_api_headers = {"apikey": self.kiwi_apikey}
        self.api_call()

    def api_call(self):
        """Function to call Kiwi API with correct headers,
        parameters, and get the response as an attribute.
        """
        response = requests.get(
            url=self.kiwi_api_url,
            params=self.kiwi_api_parameters,
            headers=self.kiwi_api_headers,
        )

        response.raise_for_status()
        self.data = response.json()
