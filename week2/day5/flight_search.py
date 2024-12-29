import requests
import os


class FlightSearch:
    # This class is responsible for talking to the Flight Search API.
    # The correct date format is dd/mm/YYYY, e.g. 29/05/2021
    """Flight Search class. Gets parameters from object to structure,
    the API query parameters and initialize the object. After,
    calls the api_call function to request data passsed at object
    initialization.
    """

    def __init__(
        self,
        fly_from,
        fly_to,
        date_from,
        date_to,
        nights_in_dst_from=7,
        nights_in_dst_to=7,
        curr="USD",
        limit=20,
        max_stopovers=0,
    ):
        self.kiwi_api_url = "https://tequila-api.kiwi.com/v2/search"
        self.kiwi_apikey = os.getenv("KIWI_API_TOKEN")
        self.fly_from = fly_from
        self.fly_to = fly_to
        self.date_from = date_from
        self.date_to = date_to
        self.nights_in_dst_from = (nights_in_dst_from,)
        self.nights_in_dst_to = nights_in_dst_to
        self.curr = curr
        self.limit = limit
        self.max_stopovers = max_stopovers
        self.data = ""

        self.kiwi_api_parameters = {
            "fly_from": self.fly_from,
            "fly_to": self.fly_to,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "nights_in_dst_from": self.nights_in_dst_from,
            "nights_in_dst_to": self.nights_in_dst_to,
            "limit": self.limit,
            "curr": self.curr,
            "max_stopovers": self.max_stopovers,
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
