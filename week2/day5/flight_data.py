import datetime


class FlightData:
    """Class to structure the flight search results."""

    # This class is responsible for structuring the flight data.

    def __init__(self, flight_results: list, desired_price=0):

        self.flight_results = flight_results
        self.desired_price = desired_price
        self.price = 0
        self.flight_data = {}
        self.structure_flight_results()

    def structure_flight_results(self):

        results_amount = len(self.flight_results["data"])

        if results_amount > 0:
            # results are sorted from lowest to highest price
            # grab the first item as it will be the lowet price
            for count, item in enumerate(self.flight_results["data"]):

                if count == 0:
                    self.route_quantity = len(item["id"].split("|"))
                    self.departure_date = (item["route"][0]["local_departure"]).split(
                        "T"
                    )[0]
                    self.return_date = (
                        item["route"][self.route_quantity - 1]["local_arrival"]
                    ).split("T")[0]
                    self.city_from = item["cityFrom"]
                    self.from_code = item["flyFrom"]
                    self.city_to = item["cityTo"]
                    self.to_code = item["flyTo"]
                    self.price = item["price"]

                    self.flight_data = {
                        "price": self.price,
                        "city_from": self.city_from,
                        "from_code": self.from_code,
                        "city_to": self.city_to,
                        "to_code": self.to_code,
                        "departure_date": self.departure_date,
                        "return_date": self.return_date,
                    }

                    # Check if price is lower than desired price
                    if self.price < self.desired_price:
                        print("Low Price Alert!")
                        print(
                            f"Only ${self.price} to fly from {self.city_from}-{self.from_code} to {self.city_to}-{self.to_code}, from {self.departure_date} to {self.return_date}"
                        )
                        # print(f"City From: {self.city_from}, City To: {self.city_to}")
                        # print(f"Price: {self.price}")
                        # print(f"Flight has {int(self.route_quantity / 2)} stops.")
                        # print(f"Dates: {self.departure_date} -> {self.return_date} ")
                        print("-" * 100)
