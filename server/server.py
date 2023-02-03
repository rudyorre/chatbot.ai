from flask import Flask
from flask_cors import CORS, cross_origin
from SPARQLWrapper import SPARQLWrapper, JSON
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
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


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
