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

    def assembly_query(self, assembly='?assembly', id='?id', mass='?mass', function='?function'):
        '''
        Creates a sparql query using the provided subject, predicate, and object variables. By default,
        these variables will be unknown.

        Args:
            assembly: an object of fse:Assembly
            id: id of assembly
            mass: mass of assembly
            function: function of assembly
        
        Returns:
            A list of dictionaries containing representing the JSON that the SPARQL query returns.
        '''
        self._sparql.setQuery(f'''
            PREFIX fse:			<http://opencaesar.io/examples/firesat/disciplines/fse/fse#>
            PREFIX base:		<http://imce.jpl.nasa.gov/foundation/base#>
            PREFIX analysis: 	<http://imce.jpl.nasa.gov/foundation/analysis#>
            PREFIX vim4: 		<http://bipm.org/jcgm/vim4#>
            PREFIX mission: 	<http://imce.jpl.nasa.gov/foundation/mission#>

            SELECT DISTINCT ?assembly ?id ?mass ?function

            WHERE {{
                {assembly} a fse:Assembly ;									# match an assembly
                        base:hasIdentifier "{id}" ;							# match its id
                        analysis:isCharacterizedBy [						# match its mass
                            vim4:hasDoubleNumber {mass}
                        ] ;
                        mission:performs {function} .						# match a function it performs
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
