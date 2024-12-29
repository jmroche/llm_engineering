import pandas


class DataManager:
    # This class is responsible for talking to the Destinatinations CSV
    """Class responsible to read and getting the destinations from file."""

    def __init__(self, file_path):
        """Initialization function. That takes the file_path
           for the destinations list as a parameter, and calls
            destinations functions to load the the data.

        Args:
            file_path ([type]): File path for the CSV file to load.
        """

        self.destination_list = []
        self.file_path = file_path
        self.destinations()  # call destinations method to load destinations_list

    def destinations(self):
        """Utilizes panda to load the CSV file into a DataFrame,
        and uses a list comprehension to create a list of dictionaries,
        each item in the cities, with IATA Codes and maximum prices for the flight.
        """

        pd = pandas.read_csv(self.file_path)
        self.destination_list = [
            {
                "City": row["City"],
                "IATA Code": row["IATA Code"],
                "Lowest Price": row["Lowest Price"],
            }
            for index, row in pd.iterrows()
        ]
