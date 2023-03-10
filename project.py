""" Hangman Game """
import random
import csv
import sys
import argparse
import requests

from tabulate import tabulate
from os import system
from time import sleep


class Round:
    def __init__(self, settings):
        # Set round customisable settings
        self.lives = settings["lives"]
        self.hangmen = load_hangmen(settings["hangmen"])

        # Get word based on topic
        match settings["topic"]:
            case "cities":
                self.word, self.hint = get_city(settings["level"])
            case _:
                self.word = get_word(settings["word_path"])
                self.hint = ""

        # Set score multiplier based on max lives
        match self.lives:
            case 10:
                self.multiplier = 1
            case 7:
                self.multiplier = 1.5
            case 5:
                self.multiplier = 3
            case _:
                sys.exit("Invalid number of lives")

        # Initialise game variables
        self.correct_guesses = []
        self.incorrect_guesses = []
        self.hidden_word = self.hide_letters()
        self.won = False

    def __str__(self):
        return (
            f"{self.hidden_word}\n"
            f"Incorrect guesses: {' '.join(sorted(self.incorrect_guesses))}\n"
            f"{self.hint}\n"
            f"{self.hangmen[self.lives]}"
            f"Lives: {self.lives}\n"
        )

    def hide_letters(self):
        """Replaces unguessed letter chars with _"""

        # Constructs new word
        hidden_word = ""
        for char in self.word:
            # Adds spaces, punctuation, etc. as per orginal word
            if char.isalpha():
                # Add char in original capitalisation if guessed else add _
                if char.lower() in self.correct_guesses:
                    hidden_word += char
                else:
                    hidden_word += "_"
            else:
                hidden_word += char

        return hidden_word

    def play(self):
        """Allow user to make a guess and check and record that guess until round is won/lost"""

        print()

        # Play round if win/lose conditions not met
        while not self.has_ended():
            # Display round information
            print(self)

            # Get guess from user
            guess = input("Guess: ").strip()
            system("clear")

            # Check and record guess
            print(self.check_guess(guess))

        self.score = self.calculate_score()
        self.end()

        return self.score

    def check_guess(self, guess):
        """Check and record user's guess"""

        # Nomarlise guesses to lowercase
        guess = guess.lower()

        # Ensure guess is not repeated
        if guess in self.correct_guesses + self.incorrect_guesses:
            return f"{guess} has been guessed previously"

        # Ensure only char is guessed
        if len(guess) != 1:
            return f"Please guess only one character at a time"

        # Ensure guessed char is a letter
        if not guess.isalpha():
            return f"Please guess only alphabet characters"

        # Check if guess is correct/wrong
        if guess in self.word.lower():
            # Record guess as correct
            self.correct_guesses.append(guess)

            # Update the hidden word
            self.hidden_word = self.hide_letters()
        else:
            # Record guess as incorrect
            self.incorrect_guesses.append(guess)

            # Reduce number of lives
            self.lives -= 1

        return ""

    def has_ended(self):
        """Check if win/lose conditions are met"""

        # End round if out of lives
        if self.lives <= 0:
            return True

        # End round if word fully guessed
        if "_" not in self.hidden_word:
            self.won = True
            return True

        # Continue round otherwise
        return False

    def calculate_score(self):
        """Calculates score for the round"""

        score = 0

        # Add 10 points per correct letter
        score += 10 * len(self.correct_guesses)

        # Add 10 points per remaining lives
        score += 10 * self.lives

        # Add up to 50 points based on remaining blanks
        blanks = 0
        for i in self.hidden_word:
            if i == "_":
                blanks += 1
        if 5 - blanks >= 0:
            score += 10 * (5 - blanks)

        return int(score * self.multiplier)

    def end(self):
        """Reveal word and congratulate winner if correctly guessed"""

        # Congratulate winner
        if self.won:
            print(self.word)
            print()
            print("🎉 Correct! 🎉")
            print()
            print("Score:", self.score)
            print()

            # https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
            # Countdown timer
            for i in range(5, 0, -1):
                print(f"Starting next round in {i}", end="\r")
                sleep(1)

        # Reveal word if wrongly guessed
        else:
            print("The word is", self.word)
            print()
            print("💀💀💀")
            print(self.hangmen[0], end="")
            print("💀💀💀")
            print()
            print("Score:", self.score)
            print()

            # Countdown timer
            for i in range(5, 0, -1):
                print(f"Showing leaderboard in {i}", end="\r")
                sleep(1)

        # Print score
        system("clear")

        return None


def main():
    # Get settings from command line arguments
    settings = get_settings()
    score = 0

    # Get username
    system("clear")
    username = input("Give me your username: ")
    system("clear")

    # Get hangman topic if not already given
    settings = set_settings(settings)

    # Play rounds until a round is lost
    while True:
        round = Round(settings)
        score += round.play()
        if not round.won:
            break

    # Update and show leaderboard
    leaderboard = update_leaderboard(username, score, settings["leaderboard_path"])
    print(tabulate(leaderboard, headers="keys", numalign="right", tablefmt="grid"))
    print(f"Your score: {score}")


def get_settings():
    """Get custom setting from command-line arguments"""

    parser = argparse.ArgumentParser(description="Play a game of hangman")
    parser.add_argument(
        "-l",
        "--lives",
        choices=[5, 7, 10],
        default=10,
        help="Number of lives per round",
        type=int,
    )
    parser.add_argument(
        "-s",
        "--style",
        choices=["default", "emoji"],
        default="default",
        help="Style of hangman display",
    )
    parser.add_argument(
        "-t",
        "--topic",
        choices=["animals", "countries", "cities"],
        help="Topic of hangman words",
    )
    parser.add_argument(
        "-lvl", "--level", choices=["1", "2", "3"], help="Level for certain topics"
    )
    args = parser.parse_args()

    level = ""

    # Validate level
    match args.topic:
        case "animals" | "countries":
            level = ""
        case "cities":
            level = args.level

    return {
        "lives": args.lives,
        "hangmen": f"./hangmen/{args.style}/{args.lives}.txt",
        "topic": args.topic,
        "level": level,
    }


def set_settings(settings):
    """Get remaining setting parameters and set corresponding file paths"""

    # Get topic if not already given
    if not settings["topic"]:
        options = {"1": "animals", "2": "countries", "3": "cities"}
        settings["topic"] = get_option("topic", options)

    # Get level/word path
    match settings["topic"]:
        case "cities":
            if not settings["level"]:
                options = {
                    "1": "≥ 5 million population",
                    "2": "≥ 2.5 million population",
                    "3": "≥ 1 thousand population",
                }
                settings["level"] = get_option("level", options)

        case "animals" | "countries":
            settings[
                "word_path"
            ] = f"./words/{settings['topic']}/{settings['topic']}.txt"

    settings[
        "leaderboard_path"
    ] = f"./leaderboards/{settings['topic']}{settings['level']}.csv"

    return settings


def get_option(param, options):
    """Prompt user until valid option given"""

    # Prompt user for valid param option
    while True:
        system("clear")
        print(f"Choose from one of the following {param}s:")
        for option in options:
            print(f"[{option}] {options[option].title()}")
        chosen_option = input(f"Option Number: ").strip().lower()
        system("clear")

        # Validate chosen option
        match param:
            case "level":
                # Returns the level number
                if chosen_option in options:
                    return chosen_option

            case "topic":
                # Returns the topic name
                if chosen_option in options:
                    return options[chosen_option]
                elif chosen_option in options.values():
                    return chosen_option


def get_word(path):
    """Gets a word from the given file path"""

    words = []

    # Check if file exists
    try:
        file = open(path)
    except FileNotFoundError:
        sys.exit("File does not exist")
    else:
        file.close()

    # Load all words into list
    with open(path) as file:
        for line in file:
            if not line.isspace():
                words.append(line.strip())

    # Return random word
    return random.choice(words)


def get_city(level):
    """Returns a random city with the given minimum population"""

    # Get country codes from file
    codes = {}
    with open("./words/cities/codes.csv") as file:
        reader = csv.DictReader(file)
        for row in reader:
            codes[row["Code"]] = row["Name"]

    # Sets population batches from which random city is chosen
    pop_batches = ["40000000", "12000000", "7650000", "6530000", "5470000"]

    if level == "2" or level == "3":
        pop_batches += [str(5000000 - 500000 * i) for i in range(6)]
    if level == "3":
        pop_batches += [str(2500000 - 100000 * i) for i in range(15)]

    max_pop = random.choice(pop_batches)

    # Query API for random city its country
    api_url = f"https://api.api-ninjas.com/v1/city?max_population={max_pop}&limit=30"
    response = requests.get(
        api_url, headers={"X-Api-Key": "MCwKDhLGR2FLu3PFHrVKCg==gmkHVRPJlEjlCbnI"}
    )
    if response.status_code == requests.codes.ok:
        city = random.choice(response.json())
        return city["name"], "Country: " + codes[city["country"]]
    else:
        print("Error:", response.status_code, response.text)
        exit("get_city request failed")


def load_hangmen(path):
    """Returns a list of hangman figures, with their index representing no. of lives remaining"""

    hangmen = ""

    # Check if file exists
    try:
        file = open(path)
    except FileNotFoundError:
        sys.exit("File does not exist")
    else:
        file.close()

    # Load hangmen figures
    with open(path) as file:
        for row in file:
            hangmen += row

    return hangmen.split(",\n")


def update_leaderboard(name, score, path):
    """Updates previous leaderboard"""

    leaderboard = [{"Rank": None, "Name": name, "Score": score}]

    # Read contents of previous leaderboard
    with open(path) as file:
        reader = csv.DictReader(file)
        for row in reader:
            leaderboard.append(row)

    # Sort new leaderboard, limiting to 10 row
    leaderboard = sorted(leaderboard, key=lambda row: int(row["Score"]), reverse=True)
    while len(leaderboard) > 10:
        leaderboard.pop(10)

    # Update rank number
    for rank, row in enumerate(leaderboard):
        row["Rank"] = rank + 1

    # Write new leaderboard into file
    with open(path, "w") as file:
        writer = csv.DictWriter(file, fieldnames=["Rank", "Name", "Score"])
        writer.writeheader()
        for row in leaderboard:
            writer.writerow(row)

    return leaderboard


if __name__ == "__main__":
    main()
