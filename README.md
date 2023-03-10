# Hangman

#### Video Demo:

#### Description:

Play a game of hangman with a few customisable settings such as:

.

1. **Topic**: which includes *animals*, *countries* and *cities*.
2. **Level**: for certain topics, namely *cities*
3. **Lives**: 10, 7, or 5 wrong guesses
4. **Style**: whether the hangman uses an O or an emoji for its face

## Files

#### project.py
Contains all the code for the hangman game, including all the functions and the Round class.

#### test_project.py
Contains unit tests to be run using pytest.

#### requirements.txt
Contains a list of all pip-installable libraries.

#### /hangmen
Folder containing TXT files with hangman figures. Name of file (e.g. 10.txt, 7.txt) represents the maximum number of lives the figures are intended to be used for.

Each hangman figure is separated by a comma on its own line (,\n) and ordered such that each figure's index corresponds to the number of remaining lives, with the 0th index corresponding to a completed figure.
* /default: Hangman figures use O for heads
* /emoji: Hangman figures use emojis like 😫 for heads

#### /leaderboards
Folder containing CSV files of the leaderboards for each topic and level (e.g. cities3.csv is the leaderboard for level 3 of topic cities). Each file contains up to ten entries consisting of their Rank, Name and Score.

#### /words
Folder containing files related to words for each hangman topic.

##### /words/animals
* animals.txt: Contains names of animals, one per line, used in the hangman game
* animals_raw.txt: Raw HTML from https://en.wikipedia.org/wiki/List_of_animal_names from which I sourced the animal names.
* parse_animals.py: Python code which uses RegEx to parse animal names from the raw HTML.

##### /words/countries
* countries.txt: Contains names of countries, one per line, used in the hangman game
* countries_raw.txt: Raw HTML from https://www.worldometers.info/geography/alphabetical-list-of-countries/ from which I sourced the country names.
* parse_countries.py: Python code which uses RegEx to parse country names from the raw HTML.

##### /words/cities
* codes.csv: Contains the ISO 3166 codes for each country, used to convert the ISO code returned from the API into their names to display as hints.
* cities.txt: Contains names and populations of cities as sample data. Was used to set the upper limits of the population batches during development.

#### /test_files
Folder containing dummy files used for testing purposes in test_project.py. Some tests will fail if this folder is absent.

## Functions & Classes
#### main()
1. Get settings from command-line arguments through get_settings
2. Set score to 0
3. Get name from user
4. Get remaining settings through set_settings()
5. Play rounds until a round is lost while tallying up the total score
6. Update the leaderboard
7. Display the leaderboard and user's score

        +--------+-----------+---------+
        |   Rank | Name      |   Score |
        +========+===========+=========+
        |      1 | Calvin    |    5160 |
        +--------+-----------+---------+
        |      2 | Calvin    |    4990 |
        +--------+-----------+---------+
        |      3 | Calvin    |    2800 |
        +--------+-----------+---------+
        |      4 | Calvin    |    1910 |
        +--------+-----------+---------+
        |      5 | Calvin    |    1830 |
        +--------+-----------+---------+
        |      6 | Calvin    |     300 |
        +--------+-----------+---------+
        |      7 | Calvin    |     190 |
        +--------+-----------+---------+
        |      8 | Ricardo   |     180 |
        +--------+-----------+---------+
        |      9 | Calvin    |     150 |
        +--------+-----------+---------+
        |     10 | Calvin    |     120 |
        +--------+-----------+---------+
        Your score: 1910

#### get_settings()
Return a settings dictionary as specified from the given command-line arguments.

Example program run command:

    $ python project.py -t cities -lvl 3 -l 5 -s emoji

Available command-line arguments:

    -l, --lives {5, 7, 10}
                Number of lives per round

    -s, --style {default, emoji}
                Style of hangman display

    -t, --topic {animals, countries, cities}
                Topic of hangman words

    -lvl, --level {1, 2, 3}
                Level for certain topics

Returned dictionary:

    {
        # Will be 10 by default
        "lives": args.lives,

        # Example: ./hangmen/default/10.txt
        "hangmen": f"./hangmen/{args.style}/{args.lives}.txt",

        # Will be None if not given
        "topic": args.topic,

        # Will be "" if not given or the topic is animals/countries
        "level": level,
    }

#### set_settings(settings)
Returns a completed settings dictionary with a *word_path* for *animals/countries* topic and a *leaderboard_path*.

*settings*: the *settings* dictionary returned from *get_settings()*

If *topic* and/or *level* is not provided as command-line arguments, user will be prompted for them until a valid option is given.

Returned dictionary:

    {
        # As set previously
        "lives": 10,

        # As set previously
        "hangmen": ./hangmen/emoji/10.txt,

        # As per user input if previously None
        "topic": animals,

        # As per user input if previously None and topic is cities
        "level": "",

        # As per topic given, example: ./words/animals/animals.txt
        "word_path": f"./words/{settings['topic']}/{settings['topic']}.txt"

        # As per topic & level given, example: ./leaderboards/animals.csv
        "leaderboard_path": f"./leaderboards/{settings['topic']}{settings['level']}.csv"
    }

#### get_option(param, options)
Returns a validated option selected by the user.

*param*: Name of setting parameter user will be prompted for (e.g. "topic" or "level")

*options*: Dictionary containing valid options, with the keys being what the user is expected to input and values being the description of said option. If *param* is *"topic"*, entering the topic name directly is also accepted.

User will be prompted repeatedly until a valid option is provided.

Example usage:

        options = {"1": "animals", "2": "countries", "3": "cities"}
        settings["topic"] = get_option("topic", options)

What will be displayed to the user:

        Choose from one of the following topics:
        [1] Animals
        [2] Countries
        [3] Cities
        Option Number:

#### get_word(path)
Returns a random word from the given file path.

*path*: path of file from which random word is taken form.

Will exit the program if FileNotFound.

Word file is treated as one word/phrase per line.

#### get_city(level)
Returns a random city and its country (as a hint) from api-ninjas.com according to the given level.

*level*: the higher the level, the lower the minimum population of the random city.

*api-ninjas.com* returns a list of cities with the most population first under the provided query. Meaning, regardless whether the minimum population set is 10 million or 1 million, the first city returned will always be Tokyo.

To make the returned city somewhat randomised, I used the *maximum population* instead in the queries. This is implemented by separating the cities into batches of roughly 30 by creating a list with the upper population limits of each batch. Then a random upper limit is selected from the list to be used in the request query.

The upper limits of each batch is set according sample data which is saved in *./words/cities/cities.txt*

    # First batch: 40 mil - 12 mil, Second batch: 12 mil - 7.65 mil, etc.
    pop_batches = ["40000000", "12000000", "7650000", "6530000", "5470000"]

    if level == "2" or level == "3":
        pop_batches += [str(5000000 - 500000 * i) for i in range(6)]
    if level == "3":
        pop_batches += [str(2500000 - 100000 * i) for i in range(15)]

#### load_hangmen(path)
Returns a list of hangman figures, with their index corresponding to the number of lives remaining.

The entire hangmen file is added to a single string before being split by *",\n"* (i.e. *hangmen.split(",\n")* ) into a list of hangmen figures.

#### update_leaderboard(name, score, path)
Returns a leaderboard dictionary after the previous leaderboard in file has been updated with the new entry. The leaderboard file is also updated in the process.

*name*: username to be saved in leaderboard

*score*: user's total score for current game

*path*: path of leaderboard file to be read and updated

The leaderboard will always be limited to a maximum of ten entries, sorted from highest score.

### class Round

The Round class contains all the attributes and methods pertaining to a single round of hangman. I used a class since there are multiple variables that need to be passed around several functions and need to be reset after each round.

#### \_\_init__(self, settings)
Initialises a round and sets its instance attributes.

*settings*: the *settings* dictionary containing the customisable settings applicable to every round of the game

The a round object will have the following attributes:
* **lives**: number of remaining lives
* **hangmen**: list of hangmen figures
* **word**: random word for current round
* **hint**: hint for word if *topic* us *cities* (e.g. "Country: CN")
* **multiplier**: score multiplier based on maximum lives
* **correct_guesses**: list of correctly guessed letters
* **incorrect_guesses**: list of incorrectly guessed letters
* **hidden_word**: word to be displayed to user with unguessed letters being replaced with _
* **won**: True/False whether round is won

#### \_\_str__(self)
Returns a string displaying information for the current round such as the hidden word, incorrect guesses, hint, the hangman figure and remaining lives.

Example:

        _uanda
        Incorrect guesses: e f i m o
        Country: Angola
        ====+-----+-----
            | /   ¦
            |/    O
            |
            |
            |
        ====+===========
        Lives: 5

        Guess:

#### hide_letters(self)
Returns a string with unguessed letters replaced with "_", ignoring non-letter characters and retaining original capitalisation.

The string is created from an empty string by adding each of the original word's characters one at a time while adding "_" in lieu of an unguessed letter.

#### play(self)
Returns the round's score after going through the playing sequence until the round is won/lost.

Playing sequence:

.

1. Display round information
2. Get guess from user
3. Check and record user's guess
4. If round has not ended, go back to step 1
5. Calculate round's score
6. End the round, displaying correct answer or congratulating the user
7. Return round's score

#### check_guess(self, guess)
Returns an empty string and records the user's guess if the guess is valid or returns an error message if the guess is invalid.

A guess is considered invalid if:

.

1. It has been guessed previously
2. It contains multiple characters
3. It is not an alphabet character

If the guess is correct, it is added to *correct_guesses* and the *hidden_word* is updated to reveal the newly guessed letter

If the guess is incorrect, it is added to *incorrect_guesses* and the *lives* is reduced by 1.

#### has_ended(self)
Returns True/False on whether the win/lose conditions have been met.

If out of lives, True is returned and *won* remains False.

If no "_" are remaining in *hidden_word* (i.e. all letters has been guessed correctly), True is returned and *won* is set to True.

Otherwise, False is returned.

#### calculate_score(self)
Returns the score for the round

Scoring:
* 10 points are added per correct letter guessed
* 10 points are added per remaining lives
* 50 points are added if no remaining "\_", else this is reduced by 10 per "\_" remaining (e.g. for "s_a_e", 30 points are added)
* The above total is then multiplied by the *multiplier* set according to the maximum number of lives

#### end(self)
Returns None, revealing the correct word if the round is lost or congratulating the user if the round is won. Round's score is also shown to the user.

Round won:

    Bandung

    🎉 Correct! 🎉

    Score: 140

    Starting next round in 5

Round lost:

    The word is Shaoyang

    💀💀💀
    ====+-----+-----
        | /   ¦
        |/    O
        |    /|\
        |    / \
        |
    ====+===========
    💀💀💀

    Score: 100

    Showing leaderboard in 5

