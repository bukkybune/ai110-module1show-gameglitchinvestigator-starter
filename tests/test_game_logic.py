from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Tests targeting the two bugs that were fixed ---

def test_too_high_message_says_lower():
    # Bug fix: "Too High" hint was showing "Go HIGHER!" instead of "Go LOWER!"
    outcome, message = check_guess(80, 50)
    assert outcome == "Too High"
    assert "LOWER" in message, f"Expected 'LOWER' in hint, got: {message}"

def test_too_low_message_says_higher():
    # Bug fix: "Too Low" hint was showing "Go LOWER!" instead of "Go HIGHER!"
    outcome, message = check_guess(20, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message, f"Expected 'HIGHER' in hint, got: {message}"

def test_single_digit_guess_vs_two_digit_secret_is_too_low():
    # Bug fix: when secret was cast to a string, str comparison made "9" > "50" == True
    # (because "9" comes after "5" alphabetically), so guess=9 secret=50 wrongly returned
    # "Too High". With the fix, numeric comparison correctly returns "Too Low".
    outcome, message = check_guess(9, 50)
    assert outcome == "Too Low", (
        f"9 < 50 should be 'Too Low', got '{outcome}'. "
        "This likely means secret is being compared as a string."
    )
