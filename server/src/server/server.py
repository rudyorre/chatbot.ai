from nlp2sparql import NaturalLanguageQueryExecutor, Query
from fuseki import FusekiClient
from frontend import FrontEnd

from flask import Flask, request
from flask_cors import CORS, cross_origin
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


@app.route("/")
@cross_origin()
def homepage():
    frontend = FrontEnd("index.html")
    return frontend.render_page()


@app.route("/query")
@cross_origin()
def query():
    sparql = SPARQLWrapper("http://host.docker.internal:3030/firesat/sparql")
    sparql.setReturnFormat(JSON)
    sparql.setQuery(
        """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		SELECT * WHERE {
		?sub ?pred ?obj .
		} LIMIT 10
		"""
    )

    result = []

    # The query data will be available at "http://localhost:8080/"
    try:
        ret = sparql.queryAndConvert()
        for r in ret["results"]["bindings"]:
            result.append(r)
    except Exception as e:
        print(e)
    return str(result)


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
		#empty hardcode response, query nlqe
		processed_query = nlqe.query(user_query)
		processed_queries.append(processed_query)
	else:
		processed_queries.append(resp)
	return "", 204

@app.route("/response")
@cross_origin()
def user_response():
    return processed_queries[-1]

def parse_user_query(user_query):
	#simplify user input
	user_query = user_query.strip().lower()
	punctuation = ['.', '!', '?']
	if user_query != '' and user_query[-1] in punctuation:
		user_query = user_query[:-1]
	return user_query

def get_hardcode_response(query):
	greetings = ['hi!', 'hi', 'hello', 'hello!', 'hello there']
	if query in greetings:
		return "Hello, welcome!"
	elif query == 'tell me about yourself':
		return 'I am an AI Chatbot interface that is here to help answer questions related to the FireSat (Fire Satallite) mission design. Feel free to ask below!'
	elif query == 'what dataset do you interact with':
		return 'I interface with the FireSat dataset.'
	else:
		return ""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
