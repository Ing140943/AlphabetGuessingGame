from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
import redis

# App
application = Flask(__name__)

# connect to MongoDB
mongoClient = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] +
                          '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get(
    "REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))

# connect to game collection in mongo db
collection_game = db.game

@application.route('/')
def index():
    body = '<h1>MongoDB Exercise - Array</h1>'
    body += '<h2>Alphabet Guessing Game v1.0</h2>'
    body += '<button> <a href="/Start/">Start</a></button>'
    body += '<p>Press start to insert the question...</>'
    return body

@application.route('/Start/')
def start():
    body = '<h2>Alphabet Guessing Game v1.0</h2>'
    game = collection_game.find_one()
    if game == None:
        mydict = {
            "question": ["_","_","_","_"], 
            "char_remain": ["*","*","*","*"], 
            "answer": [], 
            "incorrect": 0,
            "index": 0, 
            "type": False, # True = create question
            "count": 0
            }
        collection_game.insert_one(mydict)
        body += "refresh this page."

    if game != None:
        body = '<h1>Select 4 characters to make a question!</h1>'
        body += '<br></br>'
        question_text = ' '.join(game['question'])
        body += 'Question :' + question_text
        body += '<br></br>'
        body += '<a href="/path_A"><button>A</button></a>'
        body += '<a href="/path_B"><button>B</button></a>'
        body += '<a href="/path_C"><button>C</button></a>'
        body += '<a href="/path_D"><button>D</button></a>'
        if game['index'] == 4:
            collection_game.update_one({}, {"$set": {"type"  : True}})
            collection_game.update_one({}, {"$set": {"index" : 0}})
            body = '<h1>Select 4 characters to make a question!</h1>'
            body += 'Question created! Prepare for playing'
            body += '<br></br>'
            body += '<a href="/play_screen"><button> Press to go</button></a>'
            return body
    return body

@application.route('/path_A')
def routeA():
    game = collection_game.find_one()
    if game['type'] == False:
        make_question(game,'A')
        return start()
    if game['type'] == True:
        inset_answer(game,'A')
        return play_screen()


@application.route('/path_B')
def routeB():
    game = collection_game.find_one()
    if game['type'] == False:
        make_question(game,'B')
        return start()
    if game['type'] == True:
        inset_answer(game,'B')
        return play_screen()

@application.route('/path_C')
def routeC():
    game = collection_game.find_one()
    if game['type'] == False:
        make_question(game,'C')
        return start()
    if game['type'] == True:
        inset_answer(game,'C')
        return play_screen()

@application.route('/path_D')
def routeD():
    game = collection_game.find_one()
    if game['type'] == False:
        make_question(game,'D')
        return start()
    if game['type'] == True:
        inset_answer(game,'D')
        return play_screen()

def make_question(game,alphabet):
    index_now = game["index"]
    collection_game.update_one({}, {"$set": {"question." + str(index_now) : alphabet}})
    index_now += 1
    collection_game.update_one({}, {"$set": {"index" : index_now}})

def inset_answer(game,alphabet):
    index_now = game["index"]
    current_fail = game["incorrect"]
    current_count = game["count"]
    current_count += 1
    if game['question'][index_now] == alphabet:
        collection_game.update_one({}, {"$set": {"answer." + str(index_now) : alphabet}})
        index_now += 1
        collection_game.update_one({}, {"$set": {"index" : index_now}})
        collection_game.update_one({}, { "$set": { 'char_remain.' + str(index_now): "" }})
    else:
        current_fail += 1
        collection_game.update_one({}, {"$set": {"incorrect": current_fail}})
    collection_game.update_one({}, {"$set": {"count": current_count}})


@application.route('/play_screen')
def play_screen():
    collection_game = db.game
    game = collection_game.find_one()
    if game['question'] == game['answer']:
        return restartGame()
    ans_text = ' '.join(game['answer'])
    char_remain_text = ' '.join(game['char_remain'])
    body = '<h2>Alphabet Guessing Game V.1.0</h2>'
    body += "Please Choose A or B or C or D to guess."
    body += '<br> <br> '
    body += 'Answer: ' + ans_text
    body += '<br>'
    body += 'Character(s) remaining: ' + char_remain_text
    body += '<br> <br>'
    body += 'Choose:  <a href="/path_A"><button> A </button></a>' 
    body += '<a href="/path_B"><button>B</button></a>'
    body += '<a href="/path_C"><button>C</button></a>'
    body += '<a href="/path_D"><button>D</button></a>'
    body += '<br> <br>'
    body += 'Your miss answer: ' + str(game["incorrect"])
    body += '<br> <br>'
    body += 'Your trying: ' + str(game["count"] )+ ' times'
    
    return body




@application.route('/regame')
def restartGame():
    collection_game = db.game
    game = collection_game.find_one()
    body = '<h2>Congratulations!!! </h2>'
    body += '<b>You win!</b>'
    body += '<br> <br> '
    body += '<b>Number of wrong answer: </b>' + str(game['incorrect'])
    body += '<br> <br> '
    body += '<b>Number of trying: </b>' + str(game['count'])
    body += '<br> <br>'
    body += '<a href="/resetTodefault"><button> Play again! </button></a>'
    return body

@application.route('/resetTodefault')
def reset():
    collection_game = db.game
    mydict = {
        "question": ["_","_","_","_"], 
        "char_remain": ["*","*","*","*"], 
        "answer": [], 
        "incorrect": 0,
        "index": 0,
        "count":0, 
        "type": False
    }
    collection_game.update_one({}, {"$set": mydict})
    return index()

@application.route('/sample')
def sample():
    doc = db.test.find_one()
    # return jsonify(doc)
    body = '<div style="text-align:center;">'
    body += '<h1>Python</h1>'
    body += '<p>'
    body += '<a target="_blank" href="https://flask.palletsprojects.com/en/1.1.x/quickstart/">Flask v1.1.x Quickstart</a>'
    body += ' | '
    body += '<a target="_blank" href="https://pymongo.readthedocs.io/en/stable/tutorial.html">PyMongo v3.11.2 Tutorial</a>'
    body += ' | '
    body += '<a target="_blank" href="https://github.com/andymccurdy/redis-py">redis-py v3.5.3 Git</a>'
    body += '</p>'
    body += '</div>'
    body += '<h1>MongoDB</h1>'
    body += '<pre>'
    body += json.dumps(doc, indent=4)
    body += '</pre>'
    res = redisClient.set('Hello', 'World')
    if res == True:
      # Display MongoDB & Redis message.
      body += '<h1>Redis</h1>'
      body += 'Get Hello => '+redisClient.get('Hello').decode("utf-8")
    return body

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)