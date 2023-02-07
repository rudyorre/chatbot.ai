from SPARQLWrapper import SPARQLWrapper, JSON

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

class FusekiClient:
    def __init__(self, connection_string: str):
        self._sparql = SPARQLWrapper(connection_string)
        self._sparql.setReturnFormat(JSON)

    def parse(self, text: str) -> list:
        """
        Tokenizes and tags a string of words, while also filtering out stop words
        to reduce the sentence down to its most minimal form.

        Args:
            text: A string containing a raw, space-separated sentence.
                Ex: text="What is the mission description"
        
        Returns:
            A list of 2-tuples representing the filtered and tokenized sentence. Format: ("word", "parts-of-speech tag")
                Ex: [('What', 'WP'), ('mission', 'NN'), ('description', 'NN'), ('?', '.')]
        """
        # Tokenize user query
        tokens = nltk.word_tokenize(text)
        # Filter redundant words
        stop_words = stopwords.words('english')
        filtered_tokens = [t for t in tokens if t not in stop_words]
        # Tag parse
        tagged_tokens = nltk.pos_tag(filtered_tokens)
        return tagged_tokens

    def what_query(self, tagged_tokens: list):
        """
        Processes user queries that ask a basic "what" question. In the context of RDF triples, the user
        should prompt a subject and predicate, which will match all objects that match the criteria. The
        implementation will involve making a more general query initially where only the subject is included,
        which will allow us to search through all of the predicate URIs, which this function will attempt to match
        with the user's provided predicate. Every RDF triple that matches this predicate will be returned from
        this query.

        Args:
            tagged_tokens: A list of
        
        Returns:
            ...
        """
        subject = tagged_tokens[1][0] # subject: analysis, base, bundle, mission, project, etc
        predicate = tagged_tokens[2][0] # predicate: imports, description, etc
        
        self._sparql.setQuery(f"""
            PREFIX foundation:<http://imce.jpl.nasa.gov/foundation/>
            
            PREFIX imports:<http://www.w3.org/2002/07/owl#imports>
            PREFIX description:<http://purl.org/dc/elements/1.1/description>

            SELECT ?subject ?predicate ?object
            WHERE {{
                foundation:{subject} {predicate}: ?object
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

