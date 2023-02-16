from nlp2sparql import NaturalLanguageQueryExecutor
from fuseki import FusekiClient
from frontend import FrontEnd

from flask import Flask, request
import nltk
from flask_cors import CORS, cross_origin
from SPARQLWrapper import SPARQLWrapper, JSON
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def homepage():
	frontend = FrontEnd('index.html')
	return frontend.render_page()

@app.route('/query')
@cross_origin()
def query():
	sparql = SPARQLWrapper(
		"http://host.docker.internal:3030/firesat/sparql"
	)
	sparql.setReturnFormat(JSON)
	sparql.setQuery("""
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

@app.route('/python')
@cross_origin()
def python_package_test():
	a = np.ones(5)
	return np.array_str(a)

client = FusekiClient('http://host.docker.internal:3030/firesat/sparql')
nlqe = NaturalLanguageQueryExecutor(client)

user_queries = []
processed_queries = []

@app.route('/query', methods=['POST'])
@cross_origin()
def user_query():
	user_query = request.get_json()["data"]
	user_queries.append(user_query)
	processed_query = nlqe.query(user_query)
	processed_queries.append(processed_query)
	return '', 204

@app.route('/response')
@cross_origin()
def user_response():
	return processed_queries[-1]


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
