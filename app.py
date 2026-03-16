import random
import streamlit as st
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# Challenge 4: show a live score and attempts-left counter in the sidebar
st.sidebar.divider()
st.sidebar.header("📊 Stats")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

attempts_left = attempt_limit - st.session_state.attempts
st.sidebar.metric("Score", st.session_state.score)
st.sidebar.metric("Attempts left", attempts_left)

st.subheader("Make a guess")

# Challenge 4: replace plain st.info with a colour-coded range banner
st.info(f"Guess a number between **{low}** and **{high}**. You have **{attempts_left}** attempt(s) left.")

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # Collaboration note: I noticed clicking "New Game" after winning or losing had no effect.
    # I reported this to Claude, which traced the issue to status, history, and score never
    # being reset — so the app hit st.stop() immediately on every rerun. Claude also spotted
    # that the secret was hardcoded to 1-100 instead of using the selected difficulty range.
    # All four fields are now reset together so the game fully restarts.
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.score = 0
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")

    # Challenge 4: show a session summary table when the game ends
    if st.session_state.history:
        st.subheader("📋 Session Summary")
        rows = []
        for i, g in enumerate(st.session_state.history, start=1):
            if isinstance(g, int):
                diff = g - st.session_state.secret
                if diff == 0:
                    closeness = "🎯 Exact!"
                elif abs(diff) <= 3:
                    closeness = "🔥 Very hot"
                elif abs(diff) <= 10:
                    closeness = "♨️ Warm"
                elif abs(diff) <= 20:
                    closeness = "🌤️ Cool"
                else:
                    closeness = "🧊 Cold"
                direction = "✅ Correct" if diff == 0 else ("⬇️ Too High" if diff > 0 else "⬆️ Too Low")
                rows.append({"Attempt": i, "Guess": g, "Direction": direction, "How close?": closeness})
            else:
                rows.append({"Attempt": i, "Guess": str(g), "Direction": "❌ Invalid", "How close?": "—"})
        st.table(rows)

    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        # Collaboration note: hints were wrong on every second guess but correct on odd ones.
        # I asked Claude to explain why, and it identified that the original code was
        # converting the secret to a string on even attempts, causing Python to use
        # alphabetical comparison (e.g. "9" > "50" is True). Claude suggested always
        # passing the secret as an int, which I confirmed fixed the issue with a targeted
        # pytest case (test_single_digit_guess_vs_two_digit_secret_is_too_low).
        outcome, message = check_guess(guess_int, st.session_state.secret)

        # Challenge 4: colour-coded hot/cold hint with proximity emoji
        if show_hint:
            diff = abs(guess_int - st.session_state.secret)
            if outcome == "Win":
                pass  # handled below
            elif diff <= 3:
                st.error(f"🔥 Very hot! {message}")
            elif diff <= 10:
                st.warning(f"♨️ Warm! {message}")
            elif diff <= 20:
                st.info(f"🌤️ Cool... {message}")
            else:
                st.info(f"🧊 Cold! {message}")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
