import random
import re
import base64
import functools
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, g
import jwt

app = Flask(__name__)
app.secret_key = 'botilon_secret_key_2024'
STUDIO_BACKGROUND = Path(__file__).parent / 'artifacts/mockup-sandbox/src/components/mockups/templates/DarkStudioComingSoonPost-TAjGE7/assets/soc-14-bg.png'
waitlist = set()
clerk_jwks_client = None

# In-memory storage to keep track of user/guest chatbot states
SESSION_STORE = {}

# ---------------------------------------------------------------------------
# Word-matching helpers
# ---------------------------------------------------------------------------

NEGATORS = ["not", "dont", "don't", "isnt", "isn't", "never", "no", "aint", "ain't"]


def has_word(text, word):
    """True only if `word` appears in `text` as a whole word."""
    return re.search(rf"\b{re.escape(word)}\b", text.lower()) is not None


def negated(text, word):
    """True if a negating word appears within 3 words before `word`."""
    words = re.findall(r"[a-z']+", text.lower())
    if word not in words:
        return False
    i = words.index(word)
    return any(w in NEGATORS for w in words[max(0, i - 3):i])


def said_yes(text):
    """Whole-word yes check."""
    return any(has_word(text, w) for w in ["yes", "yeah", "yep", "yup", "sure", "ok", "okay"])


def said_no(text):
    """Whole-word no check. Does NOT match 'know'."""
    return any(has_word(text, w) for w in ["no", "nope", "nah"])


def get_initial_messages():
    return [
        "Hello, User! 👋",
        "I like coding! 💻",
        "Hi! I'm Botilon. What is your name?"
    ]


def _clerk_jwks():
    """Create the Clerk JWKS client lazily so local startup stays lightweight."""
    global clerk_jwks_client
    if clerk_jwks_client is None:
        publishable_key = os.environ.get("CLERK_PUBLISHABLE_KEY", "")
        encoded_domain = publishable_key.split("_", 2)[-1]
        padding = "=" * (-len(encoded_domain) % 4)
        try:
            domain = base64.urlsafe_b64decode(encoded_domain + padding).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            domain = ""
        if not domain:
            return None
        clerk_jwks_client = jwt.PyJWKClient(
            f"https://{domain}/.well-known/jwks.json"
        )
    return clerk_jwks_client


def current_user():
    """Verify the Clerk browser session cookie and return its user id."""
    token = request.cookies.get("__session")
    if not token:
        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization.removeprefix("Bearer ").strip()
    jwks_client = _clerk_jwks()
    if not token or jwks_client is None:
        return None
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except (jwt.PyJWTError, Exception):
        return None


def optional_auth(view):
    """Identify logged-in users while allowing guests through."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if user is not None:
            g.user_id = user.get("sub")
            g.is_guest = False
        else:
            g.user_id = f"guest_{request.remote_addr}"
            g.is_guest = True
        return view(*args, **kwargs)
    return wrapped


def requires_auth(view):
    """Require a valid Clerk session before serving protected app content."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("sign_in", next=request.path))
        g.user_id = user.get("sub")
        g.is_guest = False
        return view(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------------------------
# Chatbot Conversation Logic Engine
# ---------------------------------------------------------------------------

def process_message(user_input, data):
    state = data.get('state', 'greeting')
    responses = []

    if state == 'greeting':
        name = user_input.strip()
        data['name'] = name
        data['state'] = 'ask_mood'
        responses.append(f"Hello {name.upper()}! 😊")
        responses.append("How are you feeling today?")

    elif state == 'ask_mood':
        mood = user_input.lower()

        def feels(word):
            """The word is present AND not negated."""
            return has_word(mood, word) and not negated(mood, word)

        if feels("happy") or feels("good") or feels("great") or feels("fine"):
            responses.append("It is great to see you happy 😃!")
            data['mood'] = 'good'
        elif feels("excited"):
            responses.append("I am happy to hear that you are excited! 🎉")
            data['mood'] = 'good'
        elif feels("sad") or feels("bad") or feels("upset") or feels("tired"):
            responses.append("I'm sorry to hear that.")
            data['mood'] = 'low'
        elif feels("nervous") or feels("worried") or feels("scared"):
            responses.append("Sometimes I feel nervous too. Take three deep breaths.")
            responses.append("1... 2... 3... Feel better?")
            data['mood'] = 'low'
        elif negated(mood, "happy") or negated(mood, "good") or negated(mood, "great"):
            responses.append("I'm sorry to hear that.")
            data['mood'] = 'low'
        else:
            responses.append("Thank you for sharing that with me 👍.")
            data['mood'] = 'unknown'

        if data['mood'] == 'low':
            data['state'] = 'mood_followup'
            responses.append("Do you want to tell me what happened?")
        else:
            data['state'] = 'activity'
            responses.append("What do you want to do?")

    elif state == 'mood_followup':
        if said_no(user_input):
            responses.append("That's okay. You don't have to.")
        else:
            responses.append("Thank you for telling me. That sounds like a hard day.")
            responses.append("Talking to someone you trust about it can really help.")
        data['state'] = 'activity'
        responses.append("What do you want to do?")

    elif state == 'activity':
        choice = user_input.lower()
        if "play" in choice:
            data['state'] = 'play_what'
            responses.append("Nice! What game would you like to play?")
        elif "read" in choice:
            data['state'] = 'read_what'
            responses.append("What would you like to read?")
        elif "learn" in choice:
            data['state'] = 'learn_what'
            responses.append("What would you like to learn?")
        elif any(phrase in choice for phrase in ["idk", "i don't know", "i do not know"]):
            data['state'] = 'magic8'
            responses.append("We are going to play a game! 🎮🎱")
            responses.append("Ask the Magic 8 Ball a question:")
        else:
            responses.append("That is Cool. 😎")
            data['state'] = 'continue_activity'
            responses.append("Do you still want to do something? (yes/no)")

    elif state == 'play_what':
        choice2 = user_input.lower()
        if any(word in choice2 for word in ["game", "games", "video games", "anything"]):
            data['state'] = 'play_game_name'
            responses.append("What is your favorite game?")
        elif any(word in choice2 for word in ["rps", "rock", "paper", "scissors"]):
            data['state'] = 'rps_play'
            responses.append("Okay! Let's play Rock, Paper, Scissors! ✊✋✌️")
            responses.append("Choose rock, paper, or scissors:")
        elif "soccer" in choice2:
            data['state'] = 'play_soccer'
            responses.append("What is your favorite soccer team ⚽?")
        elif "football" in choice2:
            responses.append("I love football too! 🏈")
            data['state'] = 'continue_activity'
            responses.append("Do you still want to do something? (yes/no)")
        elif "sports" in choice2 or "track" in choice2:
            responses.append("Nice! Sports are great!")
            data['state'] = 'continue_activity'
            responses.append("Do you still want to do something? (yes/no)")
        else:
            responses.append("That sounds fun!")
            data['state'] = 'continue_activity'
            responses.append("Do you still want to do something? (yes/no)")

    elif state == 'play_game_name':
        choice5 = user_input.lower()
        if "roblox" in choice5:
            responses.append("Roblox is my favorite game too! ⏹️")
        elif "minecraft" in choice5:
            responses.append("La-la-la lava Ch-ch-ch chicken Steve lava is tasty Chicken Jockey 🌳🐔!")
        elif "fortnite" in choice5:
            responses.append("Bro I say let him cook 🧑‍🍳!")
        elif "chess" in choice5:
            responses.append("Wow, that is a good game — chess! ♟️")
        else:
            responses.append("Nice, that is a good game! 🎮")
        data['state'] = 'ask_rps'
        responses.append("Do you want to play Rock, Paper, Scissors? (yes/no)")

    elif state == 'ask_rps':
        if said_yes(user_input):
            data['state'] = 'rps_play'
            responses.append("Let's go! ✊✋✌️")
            responses.append("Choose rock, paper, or scissors:")
        else:
            data['state'] = 'continue_activity'
            responses.append("No problem! 😊")
            responses.append("Do you still want to do something? (yes/no)")

    elif state == 'rps_play':
        user_move = user_input.lower().strip()
        options = ["rock", "paper", "scissors"]
        if user_move in options:
            computer_move = random.choice(options)
            responses.append(f"Computer chose: {computer_move}")
            if user_move == computer_move:
                responses.append("It's a tie! 👔")
            elif (user_move == "rock" and computer_move == "scissors") or \
                 (user_move == "paper" and computer_move == "rock") or \
                 (user_move == "scissors" and computer_move == "paper"):
                responses.append("You win! 🎉")
            else:
                responses.append("The computer wins! 🤖")
            data['state'] = 'rps_again'
            responses.append("Do you want to play again? (yes/no)")
        else:
            responses.append("That's not a valid move! ❌")
            responses.append("Choose rock, paper, or scissors:")

    elif state == 'rps_again':
        if said_yes(user_input):
            data['state'] = 'rps_play'
            responses.append("Let's go again! ✊✋✌️")
            responses.append("Choose rock, paper, or scissors:")
        else:
            responses.append("Good game! 😊")
            data['state'] = 'continue_activity'
            responses.append("Do you still want to do something? (yes/no)")

    elif state == 'play_soccer':
        choice4 = user_input.lower()
        if "real madrid" in choice4:
            responses.append("Real Madrid is one of my favourite teams! ⚽")
        elif "barcelona" in choice4:
            responses.append("Barcelona is Real Madrid's Rival! 🔵🔴")
        else:
            responses.append("That is a great team! ⚽")
        data['state'] = 'continue_activity'
        responses.append("Do you still want to do something? (yes/no)")

    elif state == 'read_what':
        responses.append("Oh that is a good book — so cool! 📚")
        data['state'] = 'continue_activity'
        responses.append("Do you still want to do something? (yes/no)")

    elif state == 'learn_what':
        responses.append("That is a good thing to learn!")
        responses.append("Learning makes you smarter! 🧠")
        responses.append("Let's play a Number Guessing Game! 🎮🎯🔢")
        data['secret_number'] = random.randint(1, 100)
        data['guess_tries'] = 0
        data['state'] = 'guessing'
        responses.append("I'm thinking of a number between 1 and 100.")
        responses.append("What is your guess?")

    elif state == 'guessing':
        if user_input.strip().isdigit():
            guess = int(user_input.strip())
            data['guess_tries'] = data.get('guess_tries', 0) + 1
            secret = data.get('secret_number', 50)
            if guess < secret:
                responses.append("Too low! Try again 😔")
                responses.append("What is your guess?")
            elif guess > secret:
                responses.append("Too high! Try again 🫨")
                responses.append("What is your guess?")
            else:
                tries = data['guess_tries']
                responses.append(
                    f"You got it! 🎉 It took you {tries} "
                    f"{'try' if tries == 1 else 'tries'} — great job! 👏"
                )
                data['state'] = 'guess_again'
                responses.append("Do you want to play again? (yes/no)")
        else:
            responses.append("Please type a number between 1 and 100 🫢")
            responses.append("What is your guess?")

    elif state == 'guess_again':
        if said_yes(user_input):
            data['secret_number'] = random.randint(1, 100)
            data['guess_tries'] = 0
            data['state'] = 'guessing'
            responses.append("Let's play again! 🎮")
            responses.append("I'm thinking of a new number between 1 and 100.")
            responses.append("What is your guess?")
        else:
            responses.append("Well done! 👏")
            data['state'] = 'continue_activity'
            responses.append("Do you still want to do something? (yes/no)")

    elif state == 'magic8':
        answers = [
            "Yes, definitely!",
            "It is certain.",
            "Ask again later.",
            "Cannot predict now.",
            "No way!",
            "My sources say no.",
        ]
        responses.append(f"🎱 The Magic 8 Ball says: {random.choice(answers)}")
        data['state'] = 'magic8_again'
        responses.append("Do you want to use the Magic 8 Ball again? (yes/no)")

    elif state == 'magic8_again':
        if said_yes(user_input):
            data['state'] = 'magic8'
            responses.append("Ask the Magic 8 Ball another question:")
        else:
            responses.append("Okay! 😊")
            data['state'] = 'continue_activity'
            responses.append("Do you still want to do something? (yes/no)")

    elif state == 'continue_activity':
        if said_yes(user_input):
            data['state'] = 'activity'
            responses.append("What do you want to do?")
        elif said_no(user_input):
            data['state'] = 'dashboard'
            responses.append("Okay! Let's head to the Data Detective Dashboard 🕵️")
            responses.append("━" * 28)
            responses.append("📊  DATA DETECTIVE DASHBOARD")
            responses.append("━" * 28)
            responses.append(f"Welcome, {data.get('name', '').upper()}!")
            responses.append(
                "\nMAIN MENU\n1. Data Entry\n2. View Statistics\n"
                "3. Budget Tracker\n4. Exit Dashboard"
            )
            responses.append("Enter your choice (1-4):")
        else:
            responses.append("Please type 'yes' or 'no'.")

    elif state == 'dashboard':
        choice = user_input.strip()
        if choice == '1':
            items = ["Apples", "Books", "Shoes", "Pens", "Snacks"]
            values = [10, 3, 1, 12, 5]
            categories = ["Food", "Education", "Clothing", "Supplies", "Food"]
            responses.append("📝 Opening Data Entry....")
            table = "Item      | Value | Category\n"
            table += "----------|-------|----------\n"
            for item, value, category in zip(items, values, categories):
                table += f"{item:<10}| {value:<6}| {category}\n"
            responses.append(table)
            responses.append(
                "MAIN MENU\n1. Data Entry\n2. View Statistics\n"
                "3. Budget Tracker\n4. Exit Dashboard"
            )
            responses.append("Enter your choice (1-4):")
        elif choice == '2':
            data['state'] = 'stats_collecting'
            data['stats_values'] = []
            responses.append("📊 Opening View Statistics")
            responses.append("Enter number 1 of 5:")
        elif choice == '3':
            data['state'] = 'budget_amount'
            responses.append("💰 Opening Budget Tracker")
            responses.append("Enter an amount ($):")
        elif choice == '4':
            responses.append("Exiting Dashboard... 👋")
            data['state'] = 'canada_ask'
            responses.append("Do you want to learn about Canada? (yes/no)")
        else:
            responses.append("Invalid choice! Please enter a number from 1-4.")

    elif state == 'stats_collecting':
        try:
            number = int(user_input.strip())
            data.setdefault('stats_values', []).append(number)
            count = len(data['stats_values'])
            if count < 5:
                responses.append(f"Got it! Enter number {count + 1} of 5:")
            else:
                vals = data['stats_values']
                mean = sum(vals) / len(vals)
                sorted_values = sorted(vals)
                median = sorted_values[len(sorted_values) // 2]
                report = "📊 Statistics Report:\n"
                report += f"Data:   {vals}\n"
                report += f"Mean:   {mean:.2f}\n"
                report += f"Median: {median}\n"
                report += f"Count:  {len(vals)}"
                responses.append(report)
                data['state'] = 'dashboard'
                responses.append(
                    "MAIN MENU\n1. Data Entry\n2. View Statistics\n"
                    "3. Budget Tracker\n4. Exit Dashboard"
                )
                responses.append("Enter your choice (1-4):")
        except ValueError:
            responses.append("Invalid input. Please enter a whole number.")

    elif state == 'budget_amount':
        try:
            data['budget_amount'] = float(user_input.strip())
            data['state'] = 'budget_tax_rate'
            responses.append(f"Amount: ${data['budget_amount']:.2f}")
            responses.append("Enter the tax rate (%):")
        except ValueError:
            responses.append("Please enter a valid number.")

    elif state == 'budget_tax_rate':
        try:
            tax_rate = float(user_input.strip())
            amount = data['budget_amount']
            result = amount * (1 + tax_rate / 100)
            responses.append(f"Total after {tax_rate}% tax: ${result:.2f}")
            data['state'] = 'budget_discount_rate'
            responses.append("Enter the discount rate (%):")
        except ValueError:
            responses.append("Please enter a valid number.")

    elif state == 'budget_discount_rate':
        try:
            data['budget_discount_rate'] = float(user_input.strip())
            data['state'] = 'budget_price'
            responses.append("Enter the original price ($):")
        except ValueError:
            responses.append("Please enter a valid number.")

    elif state == 'budget_price':
        try:
            price = float(user_input.strip())
            discount_rate = data['budget_discount_rate']
            result = price * (1 - discount_rate / 100)
            responses.append(f"Price after {discount_rate}% discount: ${result:.2f}")
            data['state'] = 'budget_bill'
            responses.append("Enter the bill amount ($):")
        except ValueError:
            responses.append("Please enter a valid number.")

    elif state == 'budget_bill':
        try:
            data['budget_bill'] = float(user_input.strip())
            data['state'] = 'budget_tip_rate'
            responses.append("Enter the tip rate (%):")
        except ValueError:
            responses.append("Please enter a valid number.")

    elif state == 'budget_tip_rate':
        try:
            tip_rate = float(user_input.strip())
            bill = data['budget_bill']
            total = bill * (1 + tip_rate / 100)
            responses.append(f"Total bill with {tip_rate}% tip: ${total:.2f}")
            data['state'] = 'dashboard'
            responses.append(
                "MAIN MENU\n1. Data Entry\n2. View Statistics\n"
                "3. Budget Tracker\n4. Exit Dashboard"
            )
            responses.append("Enter your choice (1-4):")
        except ValueError:
            responses.append("Please enter a valid number.")

    elif state == 'canada_ask':
        if said_yes(user_input):
            canada = {
                'name': 'Canada',
                'population': 41000000,
                'houses': 17000000,
                'temp': '3.0°C to 3.1°C',
                'number_of_schools': 18500,
                'universities': [
                    "University of Toronto (ONTARIO/Canada)",
                    "University of British Columbia",
                    "University of Alberta",
                    "McGill University (Quebec)",
                    "University of Manitoba",
                    "University of Saskatchewan",
                    "Dalhousie University (Nova Scotia)",
                    "University of New Brunswick",
                    "Memorial University (Newfoundland & Labrador)",
                    "University of PEI (Prince Edward Island)",
                    "Yukon University",
                    "Aurora College (Northwest Territory)",
                    "Nunavut Arctic College",
                ],
                'location': '43.6622° N, 79.3944° W (University of Toronto)',
            }
            responses.append(f"🍁 The name of the country is: {canada['name']}")
            responses.append(f"🌡️ Average temperature of Canada is: {canada['temp']}")
            responses.append(f"👥 Population of Canada is: {canada['population']:,}")
            responses.append(f"🏠 Number of houses: {canada['houses']:,}")
            responses.append(
                f"🏫 Number of schools: {canada['number_of_schools']:,}"
            )
            responses.append(
                "🎓 Universities:\n"
                + "\n".join(f"  • {university}" for university in canada['universities'])
            )
            responses.append(f"📍 University of Toronto: {canada['location']}")
        elif said_no(user_input):
            responses.append("Okay 😊")
        else:
            responses.append("I don't understand, please type yes or no.")
            data['state'] = 'canada_ask'
            return responses, data
        data['state'] = 'final_subject'
        responses.append("What's your favorite subject?")

    elif state == 'final_subject':
        data['subject'] = user_input.strip()
        responses.append(f"Nice! I'll remember that you like {user_input.strip()} 📚")
        data['state'] = 'final_color'
        responses.append("What's your favorite color?")

    elif state == 'final_color':
        color = user_input.lower().strip()
        data['color'] = color
        if "blue" in color:
            responses.append("Blue is my favorite color too! 💙")
        elif "red" in color:
            responses.append("Red is such a bold color! ❤️")
        elif "green" in color:
            responses.append("Do you like grass? I am joking! 💚")
        elif "pink" in color:
            responses.append("Pink is a lovely color! 🌸")
        else:
            responses.append("That is a great color! 🎨")
        name = data.get('name', 'Friend')
        subject = data.get('subject', 'learning')
        responses.append(
            f"I know your name is {name.upper()}, you like {subject}, "
            f"and your favorite color is {color}!"
        )
        responses.append(f"Goodbye {name.upper()}! See you later! 👋")
        responses.append("I hope you enjoyed talking to me! 😊")
        responses.append("Also, check this out: https://botilon--davidaraoluwaa.replit.app")
        data['state'] = 'done'

    elif state == 'done':
        responses.append("We already said goodbye! 😄")
        responses.append("Restart the chat or start a new one from Home!")

    else:
        data['state'] = 'activity'
        responses.append("Let's pick an activity! What do you feel like doing?")

    return responses, data


# ---------------------------------------------------------------------------
# App routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    user = current_user()
    if user is None:
        return render_template('landing.html')
    clerk_pub_key = os.environ.get("CLERK_PUBLISHABLE_KEY", "")
    return render_template(
        'index.html',
        is_guest=False,
        user_id=user.get("sub"),
        clerk_publishable_key=clerk_pub_key
    )


@app.route('/chatbot')
@optional_auth
def chatbot():
    return render_template(
        'index.html',
        is_guest=g.is_guest,
        user_id=g.user_id,
        clerk_publishable_key=os.environ.get("CLERK_PUBLISHABLE_KEY", "")
    )


@app.route('/sign-in')
def sign_in():
    clerk_pub_key = os.environ.get("CLERK_PUBLISHABLE_KEY", "")
    return render_template(
        'auth.html',
        mode='sign-in',
        next_url=_safe_next_url(request.args.get('next')),
        clerk_publishable_key=clerk_pub_key
    )


@app.route('/sign-up')
def sign_up():
    clerk_pub_key = os.environ.get("CLERK_PUBLISHABLE_KEY", "")
    return render_template(
        'auth.html',
        mode='sign-up',
        next_url=_safe_next_url(request.args.get('next')),
        clerk_publishable_key=clerk_pub_key
    )


def _safe_next_url(value):
    if value and value.startswith('/') and not value.startswith('//'):
        return value
    return '/chatbot'


@app.route('/start', methods=['GET', 'POST'])
@optional_auth
def start_chat():
    uid = g.user_id
    initial_state = {'state': 'greeting'}
    SESSION_STORE[uid] = initial_state
    return jsonify({
        "messages": get_initial_messages(),
        "bot_state": initial_state,
    })


@app.route('/chat', methods=['POST'])
@optional_auth
def chat_message():
    uid = g.user_id
    payload = request.json or {}
    user_input = payload.get('message', '')
    client_state = payload.get('bot_state')

    if isinstance(client_state, dict):
        SESSION_STORE[uid] = client_state
    elif uid not in SESSION_STORE:
        SESSION_STORE[uid] = {'state': 'greeting'}

    responses, updated_state = process_message(user_input, SESSION_STORE[uid])
    SESSION_STORE[uid] = updated_state
    return jsonify({
        "messages": responses,
        "responses": responses,
        "bot_state": updated_state,
    })


@app.route('/logo')
def logo():
    """Serve the Botilon logo from the static asset directory."""
    logo_path = Path(__file__).parent / 'static' / 'botilon.png'
    if logo_path.exists():
        return send_file(logo_path, mimetype='image/png')
    return redirect("https://unsplash.com")


@app.route('/favicon.ico')
def favicon():
    return logo()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
