from project import Round, set_settings, get_word, load_hangmen, update_leaderboard
from pytest import raises


def test_set_settings():
    assert set_settings({"topic": "animals", "level": ""}) == {
        "topic": "animals",
        "level": "",
        "word_path": "./words/animals/animals.txt",
        "leaderboard_path": "./leaderboards/animals.csv",
    }
    assert set_settings({"topic": "countries", "level": ""}) == {
        "topic": "countries",
        "level": "",
        "word_path": "./words/countries/countries.txt",
        "leaderboard_path": "./leaderboards/countries.csv",
    }


def test_get_word():
    assert get_word("./words/animals/animals.txt") != None
    assert get_word("./words/countries/countries.txt") != None
    assert get_word("./test_files/dummy_word.txt") == "Dummy Word"
    with raises(SystemExit):
        get_word("./empty.txt")


def test_load_hangmen():
    assert load_hangmen("./hangmen/default/10.txt")[10] == "\n"
    assert (
        load_hangmen("./hangmen/default/10.txt")[9] == "\n\n\n\n\n\n====+===========\n"
    )
    assert (
        load_hangmen("./hangmen/default/10.txt")[0]
        == "====+-----+-----\n    | /   ¦\n    |/    O\n    |    /|\\\n    |    / \\\n    |\n====+===========\n"
    )
    assert load_hangmen("./hangmen/emoji/10.txt")[10] == "\n"
    assert load_hangmen("./hangmen/emoji/10.txt")[9] == "\n\n\n\n\n\n====+===========\n"
    assert (
        load_hangmen("./hangmen/emoji/10.txt")[0]
        == "====+-----+-----\n    | /   ¦\n    |/   💀\n    |    /|\\\n    |    / \\\n    |\n====+===========\n"
    )
    assert (
        load_hangmen("./hangmen/default/7.txt")[3]
        == "====+-----+-----\n    | /   ¦\n    |/    O\n    |\n    |\n    |\n====+===========\n"
    )
    assert (
        load_hangmen("./hangmen/emoji/5.txt")[2]
        == "====+-----+-----\n    | /   ¦\n    |/   😝\n    |     |\n    |\n    |\n====+===========\n"
    )
    with raises(SystemExit):
        load_hangmen("./empty.txt")


def test_update_leaderboard():
    assert update_leaderboard("Calvin", 100, "./test_files/dummy_board.csv")[0] == {
        "Rank": 1,
        "Name": "Calvin",
        "Score": "200",
    }
    assert update_leaderboard("Calvin", 100, "./test_files/dummy_board.csv")[2] == {
        "Rank": 3,
        "Name": "Calvin",
        "Score": "100",
    }
    assert update_leaderboard("Calvin", 50, "./test_files/dummy_board.csv")[9] == {
        "Rank": 10,
        "Name": "Calvin",
        "Score": "100",
    }


def test_Round_hide_letters():
    round = Round(
        {
            "lives": 10,
            "hangmen": "./test_files/dummy_hangman.txt",
            "topic": "test",
            "word_path": "./test_files/dummy_word.txt",
        }
    )
    assert round.hide_letters() == "_____ ____"

    round.correct_guesses = ["m"]
    assert round.hide_letters() == "__mm_ ____"

    round.correct_guesses = ["m", "a"]
    assert round.hide_letters() == "__mm_ ____"

    round.correct_guesses = ["m", "a", "d"]
    assert round.hide_letters() == "D_mm_ ___d"

    round.correct_guesses = ["m", "a", "d", "w"]
    assert round.hide_letters() == "D_mm_ W__d"

    round.correct_guesses = ["m", "a", "d", "w", "u", "o", "r", "y"]
    assert round.hide_letters() == "Dummy Word"


def test_Round_check_guess():
    round = Round(
        {
            "lives": 10,
            "hangmen": "./test_files/dummy_hangman.txt",
            "topic": "test",
            "word_path": "./test_files/dummy_word.txt",
        }
    )
    assert round.check_guess("m") == ""
    assert round.correct_guesses == ["m"]
    assert round.hidden_word == "__mm_ ____"

    assert round.check_guess("w") == ""
    assert round.correct_guesses == ["m", "w"]

    assert round.check_guess("O") == ""
    assert round.correct_guesses == ["m", "w", "o"]

    assert round.check_guess("d") == ""
    assert round.correct_guesses == ["m", "w", "o", "d"]

    assert round.check_guess("a") == ""
    assert round.correct_guesses == ["m", "w", "o", "d"]
    assert round.incorrect_guesses == ["a"]
    assert round.lives == 9

    assert round.check_guess("W") == "w has been guessed previously"
    assert round.check_guess("o") == "o has been guessed previously"
    assert round.check_guess("oa") == "Please guess only one character at a time"
    assert round.check_guess("!") == "Please guess only alphabet characters"


def test_Round_has_ended():
    round = Round(
        {
            "lives": 10,
            "hangmen": "./test_files/dummy_hangman.txt",
            "topic": "test",
            "word_path": "./test_files/dummy_word.txt",
        }
    )
    assert round.has_ended() == False

    round.lives = 5
    round.hidden_word = "D_mm_ W__d"
    assert round.has_ended() == False

    round.lives = 0
    assert round.has_ended() == True
    assert round.won == False

    round.lives = 3
    round.hidden_word = "Dummy Word"
    assert round.has_ended() == True
    assert round.won == True


def test_Round_calculate_score():
    round = Round(
        {
            "lives": 10,
            "hangmen": "./test_files/dummy_hangman.txt",
            "topic": "test",
            "word_path": "./test_files/dummy_word.txt",
        }
    )
    round.lives = 8
    round.correct_guesses = ["d", "u", "m", "y", "w", "o", "r"]
    round.hidden_word = "Dummy Word"
    assert round.calculate_score() == 200

    round.lives = 3
    round.correct_guesses = ["d", "u", "m", "y", "w", "o", "r"]
    round.hidden_word = "Dummy Word"
    assert round.calculate_score() == 150

    round.lives = 0
    round.correct_guesses = ["d", "u", "m", "y", "w", "o", "r"]
    round.hidden_word = "Dummy Word"
    assert round.calculate_score() == 120

    round.lives = 0
    round.correct_guesses = ["d", "u", "m", "y", "w", "o"]
    round.hidden_word = "Dummy Wo_d"
    assert round.calculate_score() == 100

    round.lives = 0
    round.correct_guesses = ["d", "u", "y", "w", "o"]
    round.hidden_word = "Du__y Wo_d"
    assert round.calculate_score() == 70

    round = Round(
        {
            "lives": 7,
            "hangmen": "./test_files/dummy_hangman.txt",
            "topic": "test",
            "word_path": "./test_files/dummy_word.txt",
        }
    )
    round.lives = 3
    round.correct_guesses = ["d", "u", "m", "y", "w", "o", "r"]
    round.hidden_word = "Dummy Word"
    assert round.calculate_score() == 225

    round.lives = 0
    round.correct_guesses = ["d", "u", "y", "w", "o"]
    round.hidden_word = "Du__y Wo_d"
    assert round.calculate_score() == 105

    round = Round(
        {
            "lives": 5,
            "hangmen": "./test_files/dummy_hangman.txt",
            "topic": "test",
            "word_path": "./test_files/dummy_word.txt",
        }
    )
    round.lives = 3
    round.correct_guesses = ["d", "u", "m", "y", "w", "o", "r"]
    round.hidden_word = "Dummy Word"
    assert round.calculate_score() == 450

    round.lives = 0
    round.correct_guesses = ["d", "u", "y", "w", "o"]
    round.hidden_word = "Du__y Wo_d"
    assert round.calculate_score() == 210
