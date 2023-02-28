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
    
    def set_client(self, client):
        self.client = client
    
    def set_tokens(self, tokens):
        self.tokens = tokens            
    
    def set_strategy(self, strategy):
        self._strategy = strategy

    def execute(self):
        if self._strategy == None:
            print("No strategy has been set!")
        
        return self._strategy.execute(tagged_tokens = self.tokens, cache = self.predicate_cache, client=self.client)

class NLPStrategy:
    def execute(self, tokens, cache, client):
        pass

class WhatStrategy(NLPStrategy):    

    def isURI(self, uri: str):
        return len(uri) > 2 and uri[0] == '<' and uri[-1] == '>'

    def execute(self,tagged_tokens, cache, client):
        '''
        Processes user queries that ask a basic "what" question. In the context of RDF triples, the user
        should prompt a subject and predicate, which will match all objects that match the criteria. The
        implementation will involve making a more general query initially where only the subject is included,
        which will allow us to search through all of the predicate URIs, which this function will attempt to match
        with the user's provided predicate. Every RDF triple that matches this predicate will be returned from
        this query.

        Args:
            tagged_tokens: A list of tokens
        
        Returns:
            filtered_result: A dict containing a response english string
        '''

        # Determine if subject is a uri
        subject = tagged_tokens[1][0] # subject: analysis, base, bundle, mission, project, etc
        predicate = tagged_tokens[2][0]
        if self.isURI(subject):
            db_result = client.query(subject=subject)
        else:            
            db_result = client.query(subject=f'foundation:{subject}')

        # Stemming initialization        
        ps = PorterStemmer()
        predicate = tagged_tokens[2][0]
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
                
        # TEMPORARY: code to set consistent POST response
        filtered_result2 = {}
        filtered_result2['response'] = filtered_result[0]['object']['value']
        
        return filtered_result2

class DomainRangeStrategy(NLPStrategy):
    def execute(self, tagged_tokens, cache, client):
        '''
        Processes user queries that ask a basic "domain / range" question. In the context of RDF triples, the user
        should prompt a property_label, which will match all property_labels that match the criteria and return their
        associated domain and range entries as labels or uris. Disambiguation occurs for multiple matchine property
        labels. Multi-word property labels must be wrapped in quotes.

        Args:
            tagged_tokens: A list of tokens
        
        Returns:
            filtered_result: A dict containing a response english string
        '''
        prefixes = {}
        domain = None
        range = None
        property = None
        result = None

        # DOMAIN & RANGE of property query
        if ('domain', 'NN') in tagged_tokens and ('range', 'NN') in tagged_tokens:
            # extract property index from tokens
            dom_index = tagged_tokens.index(('domain', 'NN'))
            range_index = tagged_tokens.index(('range', 'NN'))
            property_index = range_index + 1 if range_index > dom_index else dom_index + 1

            # query via property label
            prop = tagged_tokens[property_index][0].strip('"')
            result = client.domain_range_query(property_label=prop)
            # FUTURE: DISAMBIGUATION CODE -- if multiple results per label, prompt user

            filtered_result = {}
            property_label = prop
            domain_label = ""
            range_label = ""

            # assign labels for domain/range/property, o/w use uris
            for key, dic in result[0].items():
                if key == "domain" or key == "domain_label":
                    domain_label = dic['value']
                elif key == "range" or key == "range_label":
                    range_label = dic['value']
                elif key == "property" and property_label == None:
                    property_label = dic['value']
            
            filtered_result['response'] = f"For property '{property_label}', the domain is '{domain_label}' and range is '{range_label}'."
            return filtered_result
        
        # FUTURE: DOMAIN only code
        # FUTURE: RANGE only code
        # FUTURE: PROPERTIES of a certain DOMAIN code
        # FUTURE: PROPERTIES of a certain RANGE code
        # FUTURE: list all PROPERTIES with DOMAIN & RANGE code

class NaturalLanguageQueryExecutor:
    def __init__(self, client):
        self.client = client
        self.predicate_cache = dict()
        self._query_cache = dict()


    def query(self, query: Query):       
        query.set_client(self.client)          
        query.set_cache(self.predicate_cache)             
        query.set_tokens(self._parse(query.user_input))

        if (('domain', 'NN') in query.tokens) or (('range', 'NN') in query.tokens):
            query.set_strategy(DomainRangeStrategy())             
        elif query.tokens[0][0] == "What" and len(query.tokens) >= 3:            
            query.set_strategy(WhatStrategy())        
        
        return self.process_query(query)

    def process_query(self, query: Query):
        # Identifying subject and predicate
        subject = query.tokens[1][0] # subject: analysis, base, bundle, mission, project, etc
        predicate = query.tokens[2][0] # predicate: imports, description, etc

        # Checking if previous query was made already
        if (subject, predicate) in self._query_cache:
            return self._query_cache[(subject, predicate)]               
        
        return query.execute()

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
        replacements = dict()
        for i,t in enumerate(text_spaced):
            if bool(re.match(regex, t)):
                unique_string = f'SUPER_SPECIAL_UNIQUE_URL{i}'
                replacements[unique_string] = text_spaced[i]
                text_spaced[i] = unique_string

        # Replace quoted string with "quotation" string
        unique_string = None
        quote_token = ""
        in_quote = False
        quote_counter = 0
        for i,t in enumerate(text_spaced):
            if t[0] == "\"":
                unique_string = f'QUOTATION{i}'
                quote_token += t + " "
                in_quote = True
                quote_counter += 1
            elif in_quote and (t[-1] == "\"" or t[-2] == "\""):
                quote_token += t
                replacements[unique_string] = quote_token
                text_spaced[int(unique_string[-1])] = unique_string
                in_quote = False
            elif in_quote:
                quote_token += t + " "
                quote_counter += 1
        
        if quote_token:
            text_spaced = text_spaced[:-quote_counter]
        text = ' '.join(text_spaced)

        # Tokenize user query
        tokens = nltk.word_tokenize(text)

        # Replace placeholders with original links
        for i,token in enumerate(tokens):            
            if token in replacements and token.startswith("QUOTATION"):
                tokens[i] = f'{replacements[token].strip("?,.")}'
            elif token in replacements:
                tokens[i] = f'<{replacements[token]}>'

        # Filter redundant words
        stop_words = stopwords.words('english')
        filtered_tokens = [t for t in tokens if t not in stop_words]
        # Tag parse
        tagged_tokens = nltk.pos_tag(filtered_tokens)
        return tagged_tokens
    
