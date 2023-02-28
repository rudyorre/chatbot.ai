import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

class Query:
    def __init__(self, user_input):
        self.user_input = user_input        

    def set_type(self, query_type):
        self._type = query_type
    
    def set_cache(self, cache):
        self.predicate_cache = cache
    
    def set_tokens(self, tokens):
        self.tokens = tokens            
    
    def set_strategy(self, strategy):
        self._strategy = strategy

    def execute(self,db_result):
        if self._strategy == None:
            print("No strategy has been set!")
        
        return self._strategy.execute(db_result, self.tokens, self.predicate_cache)

class NLPStrategy:
    def execute(self,db_result,tokens, cache):
        pass


class WhatStrategy(NLPStrategy):    

    def execute(self,db_result,tokens, cache):
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
        # Stemming initialization
        
        ps = PorterStemmer()
        predicate = tokens[2][0]
        predicate_stem = ps.stem(predicate)        
        filtered_result = list()
        for i in range(len(db_result)):
            # Split string with delimiters ('/' and '#')
            predicate_uri = db_result[i]['predicate']['value']
            predicate_name = re.split(r'/|#', predicate_uri)[-1]
            predicate_name_stem = ps.stem(predicate_name)
        
            if predicate_name == predicate or predicate_stem == predicate_name_stem:
                cache[predicate_name] = predicate_uri
                filtered_result.append(db_result[i])
        
        return filtered_result

class NaturalLanguageQueryExecutor:
    def __init__(self, client):
        self.client = client
        self.predicate_cache = dict()
        self._query_cache = dict()


    def query(self, query: Query):       
        query.set_cache(self.predicate_cache)             
        query.set_tokens(self._parse(query.user_input))

        if query.tokens[0][0] == "What" and len(query.tokens) >= 3:            
            query.set_strategy(WhatStrategy())        
        
        return self.process_query(query)

    def process_query(self, query: Query):
        # Identifying subject and predicate
        subject = query.tokens[1][0] # subject: analysis, base, bundle, mission, project, etc
        predicate = query.tokens[2][0] # predicate: imports, description, etc

        # Checking if previous query was made already
        if (subject, predicate) in self._query_cache:
            return self._query_cache[(subject, predicate)]
        
        #Run Query        
        if self._isURI(subject):
            db_result = self.client.query(subject=subject)
        else:            
            db_result = self.client.query(subject=f'foundation:{subject}')
        
        return query.execute(db_result)

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
            if token in d:
                tokens[i] = f'<{d[token]}>'

        # Filter redundant words
        stop_words = stopwords.words('english')
        filtered_tokens = [t for t in tokens if t not in stop_words]
        # Tag parse
        tagged_tokens = nltk.pos_tag(filtered_tokens)
        return tagged_tokens
    

    def _isURI(self, uri: str):
        return len(uri) > 2 and uri[0] == '<' and uri[-1] == '>'
