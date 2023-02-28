import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict

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

        if (('mass', 'NN') in tagged_tokens) or (('function', 'NN') in tagged_tokens):
            result = self._assembly_query(tagged_tokens)
            return result

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

    def _assembly_query(self, tagged_tokens: list):
        '''
        Assembly query handles the quesition related to the "mass / function" of a particular assembly object. 
        Users should provide an assembly object with "id" specified, associated mass (int) or function (list) 
        will be returned depending on the question asked.
        Args:
            tagged_tokens: A list of tokens
        
        Returns:
            filtered_result: A dict containing a response english string
        '''

        filtered_result = {}

        result_dict = defaultdict(list)
        if ('id', 'NN') not in tagged_tokens:
            filtered_result['response'] = "Please ask the question again and contain the keyword 'id' in your question :)"
            return filtered_result

        id_index = tagged_tokens.index(('id', 'NN'))
        id = tagged_tokens[id_index + 1][0]
        results = self.client.assembly_query(id=str(id))

        filtered_result['response'] = f"For assembly object {id}: <br>\n "

        for result in results:
            for k, v in result.items():
                if ('mass', 'NN') in tagged_tokens and k == "mass":
                    if 'mass' not in result_dict:
                        result_dict['mass'].append(v['value'])
                        filtered_result['response'] += f"The mass is {float(v['value'])} kg. <br>\n "
                if ('function', 'NN') in tagged_tokens and k == "function":
                    result_dict['function'].append(v['value'])

        if "function" in result_dict:
            result_dict["function"] = [self._processURI(uri) for uri in result_dict["function"]]

            if len(result_dict["function"]) == 1: filtered_result['response'] += f"The function is: <br> "
            else: filtered_result['response'] += f"The functions are: <br> "

            tabstr = "&nbsp;" * 4
            for func in result_dict["function"]:
                filtered_result['response'] += tabstr + f"- {func} <br> "
        return filtered_result

    def _processURI(self, uri: str):
        '''
        Convert a URI that represents the function of an assembly object into NL
        '''
        _, func = uri.split('#')
        func_str = re.findall('[A-Z][^A-Z]*', func)
        func_str = [func_str[i] if i == 0 else func_str[i].lower() for i in range(len(func_str))]
        return " ".join(func_str)

    def _isURI(self, uri: str):
        return len(uri) > 2 and uri[0] == '<' and uri[-1] == '>'
