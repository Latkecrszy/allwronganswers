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


@app.route("/play")
def play():
    return render_template("play.html")


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
