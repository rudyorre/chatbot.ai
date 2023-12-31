from SPARQLWrapper import SPARQLWrapper, JSON
import re


class FusekiClient:
    def __init__(self, connection_string: str):
        self._sparql = SPARQLWrapper(connection_string)
        self._sparql.setReturnFormat(JSON)
        self._predicate_cache = dict()
        self._query_cache = dict()

    def query(self, subject="?subject", predicate="?predicate", object="?object"):
        """
        Creates a sparql query using the provided subject, predicate, and object variables. By default,
        these variables will be unknown.

        Args:
            subject:
            predicate:
            object:

        Returns:
            A list of dictionaries containing representing the JSON that the SPARQL query returns.
        """
        self._sparql.setQuery(
            f"""
            PREFIX foundation:<http://imce.jpl.nasa.gov/foundation/>
            SELECT ?subject ?predicate ?object
            WHERE {{
                {subject} {predicate} {object}
            }}
            """
        )

        result = []
        try:
            ret = self._sparql.queryAndConvert()
            for r in ret["results"]["bindings"]:
                result.append(r)
        except Exception as e:
            print(e)
        return result

    def assembly_query(
        self,
        assembly="?assembly",
        id="?id",
        mass="?mass",
        function="?function",
        decorator=None,
    ):
        """
        Creates a sparql query using the provided assembly object, id, mass and function variables. By default,
        these variables will be unknown.

        Args:
            assembly: an object of fse:Assembly
            id: id of assembly
            mass: mass of assembly
            function: function of assembly

        Returns:
            A list of dictionaries containing representing the JSON that the SPARQL query returns.
        """

        self._sparql.setQuery(
            f"""
            PREFIX fse:			<http://opencaesar.io/examples/firesat/disciplines/fse/fse#>
            PREFIX base:		<http://imce.jpl.nasa.gov/foundation/base#>
            PREFIX analysis: 	<http://imce.jpl.nasa.gov/foundation/analysis#>
            PREFIX vim4: 		<http://bipm.org/jcgm/vim4#>
            PREFIX mission: 	<http://imce.jpl.nasa.gov/foundation/mission#>
            
            SELECT DISTINCT ?assembly ?id ?mass ?function
            WHERE {{
                {assembly} a fse:Assembly ;									            # match an assembly
                        base:hasIdentifier {f"'{id}'" if decorator is None else id} ;	# match its id
                        analysis:isCharacterizedBy [						            # match its mass
                            vim4:hasDoubleNumber {mass}
                        ] ;
                        mission:performs {function} .						            # match a function it performs
                {decorator(mass) if decorator is not None else ""}
            }}
            """
        )

        result = []
        try:
            ret = self._sparql.queryAndConvert()
            for r in ret["results"]["bindings"]:
                result.append(r)
        except Exception as e:
            print(e)
        return result

    def domain_range_query(
        self,
        domain="?domain",
        property="?property",
        property_label="?property_label",
        range="?range",
    ):
        """
        Creates a sparql query using the provided domain, property, property_label, and range variables. By default,
        these variables will be unknown.

        Args:
            domain: domain field of property
            property: specified property
            property_label: specified property label
            range: range field of property

        Returns:
            A list of dictionaries containing representing the JSON that the SPARQL query returns.
        """

        self._sparql.setQuery(
            f"""
            PREFIX owl:   <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?domain ?domain_label ?property ?property_label ?range ?range_label
            WHERE {{
                {domain} a owl:Class .
                OPTIONAL {{ {domain} rdfs:label ?domain_label }}
                
                {property} rdfs:domain {domain} .
                {property} rdfs:label "{property_label}" .
                
                {property} rdfs:range {range} .
                OPTIONAL {{ {range} rdfs:label ?range_label }}
            }}

            ORDER BY ?domain
            """
        )

        result = []
        try:
            ret = self._sparql.queryAndConvert()
            for r in ret["results"]["bindings"]:
                result.append(r)
        except Exception as e:
            print(e)
        return result

    def domain_property_query(
        self,
        domain_label="?domain_label",
    ):
        """
            Creates a sparql query using the provided domain variable.

        Args:
            domain_label: domain label field of property

        Returns:
            A list of dictionaries containing representing the JSON that the SPARQL query returns.
        """

        self._sparql.setQuery(
            f"""
            PREFIX owl:   <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?domain ?property ?property_label
            WHERE {{
                ?domain a owl:Class .
                ?domain rdfs:label "{domain_label}" .

                ?property rdfs:domain ?domain .
                ?property rdfs:label ?property_label .
            }}

            ORDER BY ?domain
            """
        )

        result = []
        try:
            ret = self._sparql.queryAndConvert()
            for r in ret["results"]["bindings"]:
                result.append(r)
        except Exception as e:
            print(e)
        return result

    def range_property_query(
        self,
        range_label="?range_label",
    ):
        """
        Creates a sparql query using the provided range variable.

        Args:
            range_label: range label field of property

        Returns:
            A list of dictionaries containing representing the JSON that the SPARQL query returns.
        """

        self._sparql.setQuery(
            f"""
            PREFIX owl:   <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?range ?property ?property_label
            WHERE {{
                ?range a owl:Class .
                ?range rdfs:label "{range_label}" .

                ?property rdfs:range ?range .
                ?property rdfs:label ?property_label .
            }}

            ORDER BY ?range
            """
        )

        result = []
        try:
            ret = self._sparql.queryAndConvert()
            for r in ret["results"]["bindings"]:
                result.append(r)
        except Exception as e:
            print(e)
        return result

    def subclass_query(
        self,
        super="?super",
    ):
        """
        Creates a sparql query using the provided subclass variable.

        Args:
            super: superclass field uri

        Returns:
            A list of dictionaries containing representing the JSON that the SPARQL query returns.
        """

        self._sparql.setQuery(
            f"""
            PREFIX owl:   <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?sub ?super

            WHERE {{
                ?sub rdfs:subClassOf <{super}> .
                FILTER ( ?sub != <{super}> )
                FILTER ( isIRI(<{super}>) )
            }}

            ORDER BY ?sub
            """
        )

        result = []
        try:
            ret = self._sparql.queryAndConvert()
            for r in ret["results"]["bindings"]:
                result.append(r)
        except Exception as e:
            print(e)
        return result

    def superclass_query(
        self,
        sub="?sub",
    ):
        """
        Creates a sparql query using the provided superclass variable.

        Args:
            sub: subclass field uri

        Returns:
            A list of dictionaries containing representing the JSON that the SPARQL query returns.
        """

        self._sparql.setQuery(
            f"""
            PREFIX owl:   <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?sub ?super

            WHERE {{
                <{sub}> rdfs:subClassOf ?super .
                FILTER ( <{sub}> != ?super)
                FILTER ( isIRI(?super) )
            }}

            ORDER BY ?super
            """
        )

        result = []
        try:
            ret = self._sparql.queryAndConvert()
            for r in ret["results"]["bindings"]:
                result.append(r)
        except Exception as e:
            print(e)
        return result
