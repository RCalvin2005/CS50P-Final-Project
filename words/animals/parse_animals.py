""" Gets animal names from https://en.wikipedia.org/wiki/List_of_animal_names """
import re


animals = []

with open("animals_raw.txt") as file:
    for line in file:
        # Check for the following pattern
        """
        <tr>
        <td><a href="/wiki/Aardvark" title="Aardvark">Aardvark</a></td>

        Special Cases:
        <tr>
        <td><a href="/wiki/Bull" title="Bull">Bull</a> <br /><i>See</i> Cattle</td>

        <tr>
        <td><a href="/wiki/Domestic_pig" class="mw-redirect" title="Domestic pig">Pig</a> <i>(<a href="/wiki/List_of_pig_breeds" title="List of pig breeds">list</a>)</i><br /><i>Also see</i> Boar</td>
        """
        if line == "<tr>\n":
            animal_line = file.readline()

            # Parse animal name from line
            if matches := re.search(r"^<td><a.+?>([a-zA-Z ]+)</a>.*</td>$", animal_line):

                # Add animal name to animals list
                animals.append(matches.group(1).strip())


with open("animals.txt", "w") as file:
    for animal in animals:
        file.write(animal + "\n")
