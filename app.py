from flask import Flask, make_response, jsonify, request, render_template, redirect
from flask_pymongo import PyMongo
import json, os, dotenv, base64, re, argon2, random, string, requests
from argon2 import PasswordHasher
from flask_cors import CORS
from cryptography.fernet import Fernet

# Initialize the variables
app = Flask(__name__)
ph = PasswordHasher()
dotenv.load_dotenv()
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', None)
cors = CORS(app, resources={r'/db/*': {"origins": ["https://allwronganswers.com", "http://127.0.0.1:5000"]}})
encoder = Fernet(os.environ.get("ENCRYPT_KEY", None).encode())
mongo = PyMongo(app)

# Color scheme: #fc9003, #FFFFFF


@app.route("/host")
def host():
    return render_template("host.html")


@app.route("/join")
def join():
    return render_template("join.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signup_error")
def signup_error():
    response = make_response(redirect("/host"))
    login_db = mongo.db.login
    email = request.args.get('email').lower()
    if not re.search('^[^@ ]+@[^@ ]+\.[^@ .]{2,}$', email):
        return redirect(f'/signup?error=invalid_email')
    if login_db.find_one({'email': request.args.get('email').lower()}) is not None:
        return redirect(f'/signup?error=email_in_use')
    if request.args.get('password'):
        hasher = PasswordHasher()
        HASH = hasher.hash(request.args.get('password'))
        login_db.insert_one({'email': email, 'password': HASH})
    else:
        login_db.insert_one({'email': email})
    cookie = json.dumps({'email': email})
    cookie = str.encode(cookie)
    cookie = base64.b64encode(cookie)
    response.set_cookie('login_info', cookie, max_age=172800)
    return response


@app.route("/create")
def create():
    if request.cookies.get("login_info"):
        login_info = json.loads(request.cookies.get("login_info"))
        games = mongo.db.games
        ids = [dict(game)['id'] for game in games.find()]
        id = int("".join([str(random.randint(0, 9)) for _ in range(6)]))
        while id in ids:
            id = int("".join([str(random.randint(0, 9)) for _ in range(6)]))
        games.insert_one({"num_of_qs": request.args.get("questions"), "time_per_q": request.args.get("time"),
                          "answers_per_q": request.args.get("answers"),
                          "players": [{"username": login_info['username'], "points": 0, "streak": 0, "correct": 0}],
                          "question": 1})
        return render_template("start.html")


@app.route("/answers")
def answers():
    """answers_list = json.load(open("answers.json"))
    print(requests.get("https://opentdb.com/api.php?amount=1").json())
    for _ in range(100):
        response = requests.get("https://opentdb.com/api.php?amount=50").json()
        print(response)
        for answer in response['results']:
            if answer['correct_answer'] not in answers_list:
                answers_list.append(answer['correct_answer'])
            for i in answer['incorrect_answers']:
                if i not in answers_list:
                    answers_list.append(i)
    json.dump(answers_list, open("answers.json", "w"), indent=4)"""
    return "done"


app.register_error_handler(404, lambda e: "no")

if __name__ == "__main__":
    app.run(port=5001)
