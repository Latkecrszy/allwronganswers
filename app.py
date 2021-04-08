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
    if request.cookies.get('login_info'):
        return render_template("host.html")
    else:
        return redirect("/login?redirect=/host")


@app.route("/join")
def join():
    if request.cookies.get('login_info'):
        return render_template("join.html")
    else:
        return redirect("/login?redirect=/join")


@app.route("/play")
def play():
    if request.cookies.get('login_info'):
        login_info = json.loads(base64.b64decode(request.cookies.get('login_info')))
        games = mongo.db.games
        game = games.find_one({"id": int(request.args.get("id"))})
        if game:
            game = dict(game)
            game['players'].append({'info': login_info, "points": 0, "streak": 0, "correct": 0})
            games.find_one_and_replace({"id": int(game['id'])}, game)
            return render_template("play.html")
        return render_template("game_not_found.html")
    else:
        return redirect("/login?redirect=/join")


@app.route("/login")
def login():
    redirect_link = request.args.get("redirect") if request.args.get("redirect") else '/join'
    return render_template("login.html", redirect=redirect_link)


@app.route("/signup")
def signup():
    redirect_link = request.args.get("redirect") if request.args.get("redirect") else '/join'
    return render_template("signup.html", redirect=redirect_link)


@app.route("/signup_error")
def signup_error():
    redirect_link = f'&redirect={request.args.get("redirect")}' if request.args.get('redirect') else None
    response = make_response(redirect(request.args.get("redirect") if request.args.get('redirect') else None))
    login_db = mongo.db.login
    email = request.args.get('email').lower()
    if not re.search('^[^@ ]+@[^@ ]+\.[^@ .]{2,}$', email):
        return redirect(f'/signup?error=invalid_email{redirect_link}')
    if login_db.find_one({'email': request.args.get('email').lower()}) is not None:
        return redirect(f'/signup?error=email_in_use{redirect_link}')
    username = ''.join([i for i in request.args.get("username") if i != ' '])
    ids = [int(dict(user)['id']) for user in login_db.find() if 'id' in dict(user)]
    id = ''.join([str(random.randint(0, 10)) for _ in range(4)])
    while id in ids:
        id = ''.join([str(random.randint(0, 10)) for _ in range(4)])
    if request.args.get('password'):
        hasher = PasswordHasher()
        HASH = hasher.hash(request.args.get('password'))
        login_db.insert_one({'email': email, 'password': HASH, 'username': username, 'id': id})
    else:
        login_db.insert_one({'email': email, 'username': username, 'id': id})
    cookie = json.dumps({'email': email, 'username': username, 'id': id})
    cookie = str.encode(cookie)
    cookie = base64.b64encode(cookie)
    response.set_cookie('login_info', cookie, max_age=172800)
    return response


@app.route("/login_error")
def login_error():
    redirect_link = f'&redirect={request.args.get("redirect")}' if request.args.get('redirect') else None
    response = make_response(redirect(request.args.get("redirect") if request.args.get('redirect') else None))
    login_db = mongo.db.login
    email = request.args.get('email').lower()
    if login_db.find_one({'email': request.args.get('email').lower()}) is None:
        return redirect(f'/login?error=email_not_found{redirect_link}')
    username = dict(login_db.find_one({'email': request.args.get('email').lower()}))['username']
    id = dict(login_db.find_one({'email': request.args.get('email').lower()}))['id']
    cookie = json.dumps({'email': email, 'username': username, 'id': id})
    cookie = str.encode(cookie)
    cookie = base64.b64encode(cookie)
    response.set_cookie('login_info', cookie, max_age=172800)
    return response


@app.route("/create")
def create():
    if request.cookies.get("login_info"):
        print(json.loads(base64.b64decode(request.cookies.get('login_info'))))
        login_info = json.loads(base64.b64decode(request.cookies.get('login_info')))
        games = mongo.db.games
        ids = [dict(game)['id'] for game in games.find()]
        id = int("".join([str(random.randint(0, 9)) for _ in range(6)]))
        while id in ids:
            id = int("".join([str(random.randint(0, 9)) for _ in range(6)]))
        insert = {"num_of_qs": request.args.get("questions"), "time_per_q": request.args.get("time"),
                  "answers_per_q": request.args.get("answers"),
                  "players": [{'info': login_info, "points": 0, "streak": 0, "correct": 0}],
                  "question": 1, "id": id}
        games.insert_one(insert)
        return render_template("start.html", info=insert)


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


@app.route("/players")
def players():
    if request.args.get("id"):
        games = mongo.db.games
        return make_response(jsonify(dict(games.find_one({"id": int(request.args.get("id"))}))['players']))
    return "invalid id"


@app.route("/start")
def start():
    return render_template("start.html", id=568295)


app.register_error_handler(404, lambda e: "no")

if __name__ == "__main__":
    app.run(port=5001)
