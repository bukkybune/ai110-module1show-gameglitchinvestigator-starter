# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?

- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").
  Bug 1: Hints are backwards
  When guess > secret, the message says "Go HIGHER!" — but you guessed too high, so you should go LOWER.
  When guess < secret, the message says "Go LOWER!" — but you guessed too low, so you should go HIGHER.

  Bug 2: The "New Game" button does not actually start a new game
  Expected: clicking "New Game" after winning or losing should reset everything and let you play again.
  What actually happened: the button appeared to do nothing. The game stayed stuck on the win or loss screen.
  The root cause was that the handler never reset `st.session_state.status` back to "playing", so on every rerun the app immediately hit the `st.stop()` check and halted. The old guesses, score, and hardcoded 1–100 secret range were also never cleared.
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

  I used Claude (Claude Code) as my AI assistant throughout this project.

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

  **Correct suggestion — backwards hints fix:** I described to Claude that the hints felt wrong while playing, and it read `check_guess` in `app.py` and immediately identified that the return messages were swapped: `guess > secret` was returning "Go HIGHER!" when it should say "Go LOWER!", and vice versa. Claude suggested flipping the two message strings in the function. I verified this was correct by running the pytest tests `test_too_high_message_says_lower` and `test_too_low_message_says_higher`, both of which passed after the fix. I also confirmed it manually in the live Streamlit app by checking that guessing below the secret now correctly said "Go HIGHER!".

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

  **Misleading suggestion — the pre-existing tests:** The starter file `tests/test_game_logic.py` had three tests that Claude initially left untouched. Those tests called `check_guess` and compared the full return value against just a string (e.g. `assert result == "Win"`), not realizing `check_guess` returns a tuple `(outcome, message)`. When I ran `pytest`, all three original tests failed with `AssertionError: assert ('Win', '🎉 Correct!') == 'Win'`. The AI had not flagged this pre-existing problem when writing the new tests alongside them. I caught it by reading the failure output, then fixed each test to unpack the tuple with `outcome, message = check_guess(...)` before asserting.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

  I used two layers of verification for each fix. First, I ran `pytest tests/test_game_logic.py -v` to confirm the targeted unit tests passed. Second, I opened the live Streamlit app with `python -m streamlit run app.py`, used the Developer Debug Info panel to see the secret number, and manually submitted guesses to confirm the hints and win/lose logic behaved correctly.

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.

  The most revealing test was `test_single_digit_guess_vs_two_digit_secret_is_too_low`, which called `check_guess(9, 50)` and asserted the outcome was `"Too Low"`. Before the fix, the original code converted `secret` to a string on even attempts, so Python compared `"9" > "50"` alphabetically — which is `True` — and incorrectly returned `"Too High"`. The test failed with the old code and passed after removing the string conversion, which confirmed the root cause exactly.

- Did AI help you design or understand any tests? How?

  Yes. I asked Claude to write pytest cases that specifically targeted the two bugs we fixed. Claude explained the string-comparison mechanism behind the type-mixing bug and then wrote `test_single_digit_guess_vs_two_digit_secret_is_too_low` using `guess=9, secret=50` as the precise edge case that would expose the failure. It also wrote the two message-content tests (`test_too_high_message_says_lower`, `test_too_low_message_says_higher`) that check the hint text directly, not just the outcome label. I reviewed each test to make sure the assertion logic matched what I understood the bug to be before trusting the results.

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.

  Every time you clicked "Submit", Streamlit re-ran the entire `app.py` script from top to bottom. The line `secret = random.randint(low, high)` was not inside a session state guard, so it generated a brand new number on every rerun. Because the secret kept changing, you were essentially chasing a moving target — you could never actually win.

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

  Imagine every button click causes the whole Python script to restart from scratch, like refreshing a webpage. Any variable you created the last time the script ran is gone. `st.session_state` is like a notebook that survives those restarts — you write something in it once and it stays there across every rerun until you deliberately change or clear it.

- What change did you make that finally gave the game a stable secret number?

  The fix was wrapping the secret generation in `if "secret" not in st.session_state:` so the random number is only picked once, the very first time the app loads. Every subsequent rerun skips that line and reads the existing value from session state instead of rolling a new one.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

  Writing targeted pytest cases immediately after identifying a bug — before and after the fix. Having a test that specifically reproduces the broken behavior (like `check_guess(9, 50)` for the string-comparison bug) made it impossible to accidentally reintroduce the same bug later without noticing. I want to keep that habit of writing the test that would have caught the bug first.

- What is one thing you would do differently next time you work with AI on a coding task?

  I would run the existing tests before asking the AI to add new ones. In this project, the three starter tests were already broken (comparing a tuple to a plain string), but I only discovered that after Claude added new tests and I ran the full suite. Checking the baseline test state first would have saved that round of confusion.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

  I used to assume that if AI-generated code ran without crashing, it was probably correct. This project showed me that code can run fine and still be subtly wrong in ways that only appear under specific conditions — like a bug that only triggers on even-numbered attempts — so I now treat AI output as a starting draft that needs deliberate verification, not a finished product.
