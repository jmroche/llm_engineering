"""
Program that takes two dates or times and calculates the delta between them. 
The dates could be provided as exact dates or can be relative (e.g., 4 days, 2 weeks, or 6 months) 
"""

import datetime
from dateutil.relativedelta import relativedelta


def time_diff(start_date, end_date):
    """
    Calculates the time difference between two dates.

    Args:
        start_date (datetime): The start date.
        end_date (datetime): The end date.

    Returns:
        None (prints the time difference in days, hours, minutes, and seconds)
    """
    # Calculate the time difference

    if start_date == None:
        start_date = datetime.datetime.now().strftime("%d/%m/%Y")
    delta = end_date - start_date

    # Extract the number of days, hours, minutes, and seconds from the time difference
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60

    # Print the time difference
    print(f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds")
