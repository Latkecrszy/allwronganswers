from flask import Flask, make_response, jsonify, request, render_template, redirect
from flask_pymongo import PyMongo
import json, os, dotenv, base64, re, random, string
from argon2 import PasswordHasher
from flask_cors import CORS
from cryptography.fernet import Fernet

# Initialize the variables
app = Flask(__name__)
ph = PasswordHasher()
dotenv.load_dotenv()
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', None)
cors = CORS(app, resources={
    r'/players/*': {"origins": ["https://allwronganswers.com", "http://127.0.0.1:5001", "http://localhost:5001"]},
    r'/remove_player/*': {
        "origins": ["https://allwronganswers.com", "http://127.0.0.1:5001", "http://localhost:5001"]},
    r'/create/*': {
        "origins": ["https://allwronganswers.com", "http://127.0.0.1:5001", "http://localhost:5001"]},
    r'/started/*': {
        "origins": ["https://allwronganswers.com", "http://127.0.0.1:5001", "http://localhost:5001"]},
    r'/*': {
        "origins": ["https://allwronganswers.com", "http://127.0.0.1:5001", "http://localhost:5001"]}
})
encoder = Fernet(os.environ.get("ENCRYPT_KEY", None).encode())
mongo = PyMongo(app)


@app.route("/host")
def host():
    if request.cookies.get('login_info'):
        login_info = json.loads(base64.b64decode(request.cookies.get('login_info')))
        if request.args.get("id"):
            response = make_response(render_template("start.html", id=int(request.args.get("id")), player_id=int(login_info["id"]),
                                   host="true"))
            response.set_cookie('host', str.encode(json.dumps("true")), max_age=172800)
            return response
        return render_template("host.html")
    else:
        return redirect("/login?redirect=/host")


@app.route("/join")
def join():
    try:
        if not request.args:
            return render_template("join.html")
        login_info = json.loads(base64.b64decode(request.cookies.get('login_info')))
        if mongo.db.games.find_one({"id": int(request.args.get("id"))}):
            return render_template("start.html", id=int(request.args.get("id")), player_id=int(login_info["id"]), host="false")
        return redirect("/game_not_found")
    except:
        return redirect("/login?redirect=/join")


@app.route("/play")
def play():
    login_info = json.loads(base64.b64decode(request.cookies.get('login_info')))
    mongo.db.games.find_one_and_update({"id": int(request.args.get("id"))}, {"$set": {"started": "true"}})
    game = mongo.db.games.find_one({"id": int(request.args.get("id"))})
    return render_template("play.html", player_id=int(login_info['id']), id=int(request.args.get("id")),
                           host=json.loads(request.cookies.get("host")), question_num=int(game['question']),
                           time=int(game['time_per_q']), num_of_questions=int(game['num_of_qs']),
                           question=game['questions'][str(game['question'])]['question'],
                           answers=game['questions'][str(game['question'])]['answers'])


@app.route("/started")
def started():
    return jsonify({"started": mongo.db.games.find_one({"id": int(request.args.get("id"))})['started']})


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


@app.route("/create", methods=["POST", "GET"])
def create():
    if request.cookies.get("login_info"):
        print(json.loads(base64.b64decode(request.cookies.get('login_info'))))
        login_info = json.loads(base64.b64decode(request.cookies.get('login_info')))
        games = mongo.db.games
        id = int("".join([str(random.randint(0, 9)) for _ in range(6)]))
        while id in [dict(game)['id'] for game in games.find()]:
            id = int("".join([str(random.randint(0, 9)) for _ in range(6)]))
        questions = {str(x): {"question": random.choice(json.load(open("questions.json"))), "answers": [random.choice(json.load(open("answers.json"))) for _ in range(int(request.args.get("answers")))]} for x in range(1, int(request.args.get("questions"))+1)}
        insert = {"num_of_qs": request.args.get("questions"), "time_per_q": request.args.get("time"),
                  "answers_per_q": request.args.get("answers"),
                  "players": [{'info': login_info, "points": 0, "streak": 0, "correct": 0, 'answer': 0, 'host': 'true'}],
                  "question": 1, "id": id, 'started': 'false',
                  'questions': questions}
        games.insert_one(insert)
        response = make_response(jsonify({"id": id}))
        response.set_cookie('host', str.encode(json.dumps("true")), max_age=172800)
        return response


@app.route("/add_player")
def add_player():
    login_info = json.loads(base64.b64decode(request.cookies.get('login_info')))
    game_players = mongo.db.games.find_one({"id": int(request.args.get("id"))})['players']
    game_players.append({'info': login_info, "points": 0, "streak": 0, "correct": 0, 'answer': 0, 'host': 'false'})
    mongo.db.games.find_one_and_update({"id": int(request.args.get("id"))}, {"$set": {"players": game_players}})
    response = make_response(jsonify({'info': login_info, "points": 0, "streak": 0, "correct": 0, 'answer': 0, 'host': 'false'}))
    response.set_cookie('host', str.encode(json.dumps("false")), max_age=172800)
    return response


@app.route("/answers")
def answers():
    return jsonify([random.choice(json.load(open("answers.json"))) for _ in range(4)])


@app.route("/questions")
def question():
    return jsonify(random.choice(json.load(open("questions.json"))))


@app.route("/game")
def game():
    games = mongo.db.games
    game = games.find_one({"id": int(request.args.get("id"))})
    return jsonify(game)


@app.route("/players")
def players():
    if request.args.get("id"):
        games = mongo.db.games
        return make_response(jsonify(dict(games.find_one({"id": int(request.args.get("id"))}))['players']))
    return "invalid id"


@app.route("/remove_player", methods=["GET", "POST"])
def remove_player():
    games = mongo.db.games
    game = games.find_one({"id": int(request.args.get("id"))})
    if game:
        game['players'] = [player for player in game['players'] if
                           int(request.args.get("player_id")) != int(player['info']['id']) or 'host' in player]
        games.find_one_and_replace({'id': int(game['id'])}, game)
        return 200
    return "no game"


@app.route("/player")
def player():
    games = mongo.db.games
    game = games.find_one({"id": int(request.args.get("id"))})
    if game:
        return jsonify([player for player in game['players'] if int(player['info']['id']) == int(request.args.get("player_id"))][0])


@app.route("/correct")
def correct():
    games = mongo.db.games
    game = games.find_one({"id": int(request.args.get("id"))})
    if game:
        game_player = [player for player in game['players'] if int(player['info']['id']) == int(request.args.get("player_id"))][0]
        game_player['points'] += int(request.args.get("points"))
        game_player['correct'] += 1
        game_player['streak'] += 1
        game_players = [player for player in game['players'] if
                        int(player['info']['id']) != int(request.args.get("player_id"))]
        game_players.append(game_player)
        game['players'] = game_players
        games.find_one_and_replace({"id": game['id']}, dict(game))



@app.route("/deleteall")
def deleteall():
    for document in mongo.db.games.find():
        mongo.db.games.find_one_and_delete(dict(document))
    return 'done'




app.register_error_handler(404, lambda e: "no")

if __name__ == "__main__":
    app.run(port=5001)
