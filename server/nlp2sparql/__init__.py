import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

class NaturalLanguageQueryExecutor:
    def __init__(self, client):
        self.client = client
        self._predicate_cache = dict()
        self._query_cache = dict()

    def query(self, text: str):
        tagged_tokens = self._parse(text)
	
        if tagged_tokens[0][0] == "What" and len(tagged_tokens) >= 3:
            result = self._what_query(tagged_tokens)
            return result
        
        return "Failed to process query :("

    def _parse(self, text: str) -> list:
        '''
        Tokenizes and tags a string of words, while also filtering out stop words
        to reduce the sentence down to its most minimal form.

        Args:
            text: A string containing a raw, space-separated sentence.
                Ex: text="What is the mission description"
        
        Returns:
            A list of 2-tuples representing the filtered and tokenized sentence. Format: ("word", "parts-of-speech tag")
                Ex: [('What', 'WP'), ('mission', 'NN'), ('description', 'NN'), ('?', '.')]
        '''
        # Replace all urls with "unique" string
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        urls = re.findall(regex, text)
        text_spaced = text.split(' ')
        d = dict()
        for i,t in enumerate(text_spaced):
            if bool(re.match(regex, t)):
                unique_string = f'SUPER_SPECIAL_UNIQUE_URL{i}'
                d[unique_string] = text_spaced[i]
                text_spaced[i] = unique_string
        text = ' '.join(text_spaced)

        # Tokenize user query
        tokens = nltk.word_tokenize(text)

        # Replace placeholders with original links
        for i,token in enumerate(tokens):
            print(token, d)
            if token in d:
                tokens[i] = f'<{d[token]}>'

        # Filter redundant words
        stop_words = stopwords.words('english')
        filtered_tokens = [t for t in tokens if t not in stop_words]
        # Tag parse
        tagged_tokens = nltk.pos_tag(filtered_tokens)
        return tagged_tokens

    def _what_query(self, tagged_tokens: list):
        '''
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
        '''
        # Identifying subject and predicate
        subject = tagged_tokens[1][0] # subject: analysis, base, bundle, mission, project, etc
        predicate = tagged_tokens[2][0] # predicate: imports, description, etc

        # Stemming initialization
        ps = PorterStemmer()
        predicate_stem = ps.stem(predicate)

        # Checking if previous query was made already
        if (subject, predicate) in self._query_cache:
            return self._query_cache[(subject, predicate)]
        
        # 
        if self._isURI(subject):
            result = self.client.query(subject=subject)
        else:
            result = self.client.query(subject=f'foundation:{subject}')

        filtered_result = list()
        for i in range(len(result)):
            # Split string with delimiters ('/' and '#')
            predicate_uri = result[i]['predicate']['value']
            predicate_name = re.split(r'/|#', predicate_uri)[-1]
            predicate_name_stem = ps.stem(predicate_name)
            if predicate_name == predicate or predicate_stem == predicate_name_stem:
                self._predicate_cache[predicate_name] = predicate_uri
                filtered_result.append(result[i])

        return filtered_result

    def _isURI(self, uri: str):
        return len(uri) > 2 and uri[0] == '<' and uri[-1] == '>'
