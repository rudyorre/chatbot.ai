from nlp2sparql import NaturalLanguageQueryExecutor, Query
from fuseki import FusekiClient
from frontend import FrontEnd

from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


@app.route("/")
@cross_origin()
def homepage():
    frontend = FrontEnd("index.html")
    return frontend.render_page()


client = FusekiClient("http://host.docker.internal:3030/firesat/sparql")
nlqe = NaturalLanguageQueryExecutor(client)

user_queries = []
processed_queries = []


@app.route("/query", methods=["POST"])
@cross_origin()
def user_query():
    querystr = request.get_json()["data"]
    user_query = Query(querystr)
    user_queries.append(user_query)

    transformed_query = parse_user_query(querystr)
    resp = get_hardcode_response(transformed_query)
    resp = {"response": resp}

    if resp["response"] == "":
        # empty hardcode response, query nlqe
        processed_query = nlqe.query(user_query)
        processed_queries.append(processed_query)
    else:
        processed_queries.append(resp)
    return "", 204


@app.route("/response")
@cross_origin()
def user_response():
    return processed_queries[-1]


####Test Endpoints####
test_client = FusekiClient("http://localhost:3030/firesat/sparql")
test_nlqe = NaturalLanguageQueryExecutor(test_client)

test_user_queries = []
test_processed_queries = []


@app.route("/testQuery", methods=["POST"])
@cross_origin()
def test_user_query():
    querystr = request.get_json()["data"]
    user_query = Query(querystr)
    test_user_queries.append(user_query)

    transformed_query = parse_user_query(querystr)
    resp = get_hardcode_response(transformed_query)
    resp = {"response": resp}

    if resp["response"] == "":
        # empty hardcode response, query nlqe
        processed_query = test_nlqe.query(user_query)
        test_processed_queries.append(processed_query)
    else:
        test_processed_queries.append(resp)
    return "", 204


@app.route("/testResponse")
@cross_origin()
def test_user_response():
    return test_processed_queries[-1]


####End ofTest Endpoints####


def parse_user_query(user_query):
    # simplify user input
    user_query = user_query.strip().lower()
    punctuation = [".", "!", "?"]
    if user_query != "" and user_query[-1] in punctuation:
        user_query = user_query[:-1]
    return user_query


def get_hardcode_response(query):
    greetings = ["hi!", "hi", "hello", "hello!", "hello there"]
    if query in greetings:
        return "Hello, welcome!"
    elif query == "tell me about yourself":
        return "I am an AI Chatbot interface that is here to help answer questions related to the FireSat (Fire Satallite) mission design. Feel free to ask below!"
    elif query == "what dataset do you interact with":
        return "I interface with the FireSat dataset."
    else:
        return ""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
