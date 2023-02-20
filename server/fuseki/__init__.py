from SPARQLWrapper import SPARQLWrapper, JSON
import re

class FusekiClient:
    def __init__(self, connection_string: str):
        self._sparql = SPARQLWrapper(connection_string)
        self._sparql.setReturnFormat(JSON)
        self._predicate_cache = dict()
        self._query_cache = dict()

    def query(self, subject='?subject', predicate='?predicate', object='?object'):
        '''
        Creates a sparql query using the provided subject, predicate, and object variables. By default,
        these variables will be unknown.

        Args:
            subject:
            predicate:
            object:
        
        Returns:
            A list of dictionaries containing representing the JSON that the SPARQL query returns.
        '''
        self._sparql.setQuery(f'''
            PREFIX foundation:<http://imce.jpl.nasa.gov/foundation/>
            SELECT ?subject ?predicate ?object
            WHERE {{
                {subject} {predicate} {object}
            }}
            '''
        )
        
        result = []
        try:		
            ret = self._sparql.queryAndConvert()	
            for r in ret["results"]["bindings"]:
                result.append(r)
        except Exception as e:
            print(e)
        return result
