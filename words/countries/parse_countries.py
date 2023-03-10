""" Gets country names from https://www.worldometers.info/geography/alphabetical-list-of-countries/ """
import re


countries = []

with open("countries_raw.txt") as file:
    line = file.readline()
    # Check for the following pattern
    """<td style="font-weight: bold; font-size:15px">Afghanistan</td>"""

    # Parse animal name from line
    countries = re.findall(r"<td style=\"font-weight: bold; font-size:15px\">(.+?)</td>", line)


with open("countries.txt", "w") as file:
    for country in countries:
        file.write(country + "\n")
