import re
import nltk
from enum import Enum
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

from collections import defaultdict


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

        return self._strategy.execute(
            tagged_tokens=self.tokens, cache=self.predicate_cache, client=self.client
        )


class NLPStrategy:
    def execute(self, tokens, cache, client):
        pass


class WhatStrategy(NLPStrategy):
    def isURI(self, uri: str):
        return len(uri) > 2 and uri[0] == "<" and uri[-1] == ">"

    def execute(self, tagged_tokens, cache, client):
        """
        Processes user queries that ask a basic "what" question. In the context of RDF triples, the user
        should prompt a subject and predicate, which will match all objects that match the criteria. The
        implementation will involve making a more general query initially where only the subject is included,
        which will allow us to search through all of the predicate URIs, which this function will attempt to match
        with the user's provided predicate. Every RDF triple that matches this predicate will be returned from
        this query.

        Args:
            tagged_tokens: A list of tokens
            status: A boolean for whether query requires disambiguation

        Returns:
            filtered_result: A dict containing a response english string
        """

        # Determine if subject is a uri
        subject = tagged_tokens[1][
            0
        ]  # subject: analysis, base, bundle, mission, project, etc
        predicate = tagged_tokens[2][0]
        if self.isURI(subject):
            db_result = client.query(subject=subject)
        else:
            db_result = client.query(subject=f"foundation:{subject}")

        # Stemming initialization
        ps = PorterStemmer()
        predicate = tagged_tokens[2][0]
        predicate_stem = ps.stem(predicate)
        filtered_result = list()
        for i in range(len(db_result)):
            # Split string with delimiters ('/' and '#')
            predicate_uri = db_result[i]["predicate"]["value"]
            predicate_name = re.split(r"/|#", predicate_uri)[-1]
            predicate_name_stem = ps.stem(predicate_name)

            if predicate_name == predicate or predicate_stem == predicate_name_stem:
                cache[predicate_name] = predicate_uri
                filtered_result.append(db_result[i])

        # TEMPORARY: code to set consistent POST response
        filtered_result2 = {}
        filtered_result2["response"] = filtered_result[0]["object"]["value"]

        return (filtered_result2, 1)


class DomainRangePropertyStrategy(NLPStrategy):
    _disambiguation_options = {}
    _disambiguation_prop_label = {}

    def _send_domain_range_properties_error(self):
        """
        Send back a response message to the user asking them to reformat their domain/range query.

        Returns:
            filtered_result: A dictionary of a response
        """
        filtered_result = {}
        filtered_result[
            "response"
        ] = f"Sorry, phrase your query as 'What are the properties of domain/range __?'"
        return filtered_result

    def execute(self, tagged_tokens, cache, client):
        """
        Processes user queries that ask about the properties of a particular "domain / range". In the context of RDF triples,
        the user should prompt a domain/range label, which will return all property_labels that match the criteria and return their
        associated property entries as labels or uris. Multi-word property labels must be wrapped in quotes.

        Args:
            tagged_tokens: A list of tokens

        Returns:
            filtered_result: A dict containing a response english string
            status: A boolean for whether query requires disambiguation
        """
        filtered_result = {}

        # extract domain OR range index from tokens
        domain_index = -1
        range_index = -1
        try:
            domain_index = tagged_tokens.index(("domain", "VBP"))
        except ValueError:
            try:
                domain_index = tagged_tokens.index(("domain", "NN"))
            except ValueError:
                domain_index = -1

        try:
            range_index = tagged_tokens.index(("range", "VBP"))
        except ValueError:
            try:
                range_index = tagged_tokens.index(("range", "NN"))
            except ValueError:
                range_index = -1

        label_index = (
            domain_index + 1 if domain_index > range_index else range_index + 1
        )

        # 1) DOMAIN PROPERTIES QUERY
        if range_index == -1:
            # short-circuit domain_range error for poorly formatted input
            if label_index >= len(tagged_tokens):
                filtered_result = self._send_domain_range_properties_error()
                return (filtered_result, 1)

            # query via domain label
            domain_label = tagged_tokens[label_index][0].strip('"')
            result = client.domain_property_query(domain_label=domain_label)
            filtered_result = {}
            property_labels = []

            # NO RESULTS
            if len(result) == 0:
                filtered_result[
                    "response"
                ] = f"Unable to find information about domain {domain_label}"
                return (filtered_result, 1)

            # extract property labels for specified domain_label
            for entity in result:
                for key, dic in entity.items():
                    if key == "property_label":
                        property_labels.append(dic["value"])

            # create response object with all labels
            collected_response = f"For domain '{domain_label}', the properties are: "
            for plabel in property_labels[:-1]:
                collected_response += f"{plabel}, "
            collected_response += (
                "" if len(property_labels) < 1 else f"{property_labels[-1]}."
            )

            filtered_result["response"] = collected_response
            return (filtered_result, 1)

        # 2) RANGE PROPERTIES QUERY
        elif domain_index == -1:
            # short-circuit domain_range error for poorly formatted input
            if label_index >= len(tagged_tokens):
                filtered_result = self._send_domain_range_properties_error()
                return (filtered_result, 1)

            # query via domain label
            range_label = tagged_tokens[label_index][0].strip('"')
            result = client.range_property_query(range_label=range_label)
            filtered_result = {}
            property_labels = []

            # NO RESULTS
            if len(result) == 0:
                filtered_result[
                    "response"
                ] = f"Unable to find information about range {range_label}"
                return (filtered_result, 1)

            # extract property labels for specified domain_label
            for entity in result:
                for key, dic in entity.items():
                    if key == "property_label":
                        property_labels.append(dic["value"])

            # create response object with all labels
            collected_response = f"For range '{range_label}', the properties are: "
            for plabel in property_labels[:-1]:
                collected_response += f"{plabel}, "
            collected_response += (
                "" if len(property_labels) < 1 else f"{property_labels[-1]}."
            )

            filtered_result["response"] = collected_response
            return (filtered_result, 1)


class DomainRangeStrategy(NLPStrategy):
    _disambiguation_options = {}
    _disambiguation_prop_label = {}

    def _clear_disambiguation_cache(self):
        """
        Clear disambiguation cache options and property label
        """
        # reset disambiguation variables
        self._disambiguation_options.clear()
        self._disambiguation_prop_label.clear()

    def _assign_labels(self, prop, result):
        """
        Extract domain, range, labels from Fuseki result object.
        Args:
            result: A json fuseki object

        Returns:
            property_label: A string of the property label
            domain_label: A string of the domain label
            range_label: A string of the range label
        """
        filtered_result = {}
        property_label = prop
        domain_label = ""
        range_label = ""

        # assign labels for domain/range/property, o/w use uris
        for key, dic in result[0].items():
            if key == "domain" or key == "domain_label":
                domain_label = dic["value"]
            elif key == "range" or key == "range_label":
                range_label = dic["value"]
            elif key == "property" and property_label == None:
                property_label = dic["value"]

        return (property_label, domain_label, range_label)

    def _show_all(self, client, prop):
        """
        Show all property/domain/range labels from Fuseki result object.
        Args:
            client: A Fuseki client
            prop: A string property label

        Returns:
            filtered_result: A dictionary of a response
        """
        filtered_result = {}
        collected_response = ""
        # iterate over each property data source
        for src, value in self._disambiguation_options.items():
            selected_uri = value
            result = client.domain_range_query(
                property=selected_uri, property_label=prop
            )
            property_label, domain_label, range_label = self._assign_labels(
                prop, result
            )
            collected_response += f"For property '{property_label}' in {src}, the domain is '{domain_label}' and range is '{range_label}'. "

        filtered_result["response"] = collected_response

        # reset disambiguation variables
        self._disambiguation_options.clear()
        self._disambiguation_prop_label.clear()

        return filtered_result

    def _send_domain_range_error(self):
        """
        Send back a response message to the user asking them to reformat their domain/range query.

        Returns:
            filtered_result: A dictionary of a response
        """
        filtered_result = {}
        filtered_result[
            "response"
        ] = f"Sorry, phrase your query as 'What is the domain and range of __?'"
        return filtered_result

    def execute(self, tagged_tokens, cache, client):
        """
        Processes user queries that ask a basic "domain / range" question. In the context of RDF triples, the user
        should prompt a property_label, which will match all property_labels that match the criteria and return their
        associated domain and range entries as labels or uris. Disambiguation occurs for multiple matchine property
        labels. Multi-word property labels must be wrapped in quotes.

        Args:
            tagged_tokens: A list of tokens

        Returns:
            filtered_result: A dict containing a response english string
            status: A boolean for whether query requires disambiguation
        """
        filtered_result = {}

        # (1) DISAMBIGUATION state
        if self._disambiguation_options and tagged_tokens:
            # SUCCESS match single option
            if tagged_tokens[0] in self._disambiguation_options:
                selected_uri = self._disambiguation_options[tagged_tokens[0]]
                result = client.domain_range_query(
                    property=selected_uri,
                    property_label=self._disambiguation_prop_label["prop"],
                )
                property_label, domain_label, range_label = self._assign_labels(
                    self._disambiguation_prop_label["prop"], result
                )
                filtered_result[
                    "response"
                ] = f"For property '{property_label}' in {tagged_tokens[0]}, the domain is '{domain_label}' and range is '{range_label}'."
                self._clear_disambiguation_cache()
                return (filtered_result, 1)

            # SUCCESS match all-of-the-above option
            elif tagged_tokens[0] == "all of the above":
                filtered_result = self._show_all(
                    client, self._disambiguation_prop_label["prop"]
                )
                return (filtered_result, 1)

            # FAIL match option
            else:
                filtered_result[
                    "response"
                ] = f"Sorry, which data source would you like for domain/range querying?"
                return (filtered_result, 0)

        # (2) DOMAIN & RANGE of property query
        elif ("domain", "NN") in tagged_tokens or ("range", "NN") in tagged_tokens:
            domain_and_range = ("domain", "NN") in tagged_tokens and (
                "range",
                "NN",
            ) in tagged_tokens
            domain_only = ("domain", "NN") in tagged_tokens and (
                "range",
                "NN",
            ) not in tagged_tokens
            range_only = ("domain", "NN") not in tagged_tokens and (
                "range",
                "NN",
            ) in tagged_tokens

            # extract property index from tokens
            dom_index = -1
            range_index = -1
            try:
                dom_index = tagged_tokens.index(("domain", "NN"))
            except ValueError:
                dom_index = -1
            try:
                range_index = tagged_tokens.index(("range", "NN"))
            except ValueError:
                range_index = -1
            property_index = (
                range_index + 1 if range_index > dom_index else dom_index + 1
            )

            # short-circuit domain_range error for poorly formatted input
            if property_index >= len(tagged_tokens):
                filtered_result = self._send_domain_range_error()
                return (filtered_result, 1)

            # query via property label
            prop = tagged_tokens[property_index][0].strip('"')
            result = client.domain_range_query(property_label=prop)
            # NO RESULTS
            if len(result) == 0:
                filtered_result[
                    "response"
                ] = f"Unable to find information for domain/range of '{prop}'"
                return (filtered_result, 1)

            property_label, domain_label, range_label = self._assign_labels(
                prop, result
            )

            # (a) DISAMBIGUATION LOGIC -- if multiple results per label, prompt user
            if len(result) > 1:
                # prepare disambiguation prompt
                tabstr = "&nbsp;" * 4
                filtered_result[
                    "response"
                ] = f"For property '{property_label}', which data source are you referring to: <br>"

                # cache uri options and extract relevant part of uri for property source
                for item in result:
                    property_label, domain_label, range_label = self._assign_labels(
                        prop, result
                    )
                    uri = item["property"]["value"]
                    src_start = uri.index("//") + 2
                    src_end = uri.index("#")
                    filtered_result["response"] += (
                        tabstr + f"- {uri[src_start:src_end]} <br>"
                    )
                    self._disambiguation_options[uri[src_start:src_end]] = f"<{uri}>"

                # check to see if uris are the same
                same_uris = False
                if len(self._disambiguation_options.items()) == 1:
                    test_val = list(self._disambiguation_options.values())[0]
                    same_uris = all(
                        val == test_val for val in self._disambiguation_options.values()
                    )

                # (i) Show all results if property uris are same
                if same_uris:
                    filtered_result = {}
                    collected_response = ""

                    # collect domain/range/property label information over each result entity
                    for entity in result:
                        property_label, domain_label, range_label = prop, "", ""
                        for key, dic in entity.items():
                            if key == "domain" or key == "domain_label":
                                domain_label = dic["value"]
                            elif key == "range" or key == "range_label":
                                range_label = dic["value"]
                            elif key == "property" and property_label == None:
                                property_label = dic["value"]

                        # return necessary information
                        if domain_and_range:
                            collected_response += f"For property '{property_label}', the domain is '{domain_label}' and range is '{range_label}'. "
                        elif domain_only:
                            collected_response += f"For property '{property_label}', the domain is '{domain_label}'. "
                        elif range_only:
                            collected_response += f"For property '{property_label}', the range is '{range_label}'. "

                    filtered_result["response"] = collected_response

                    # reset disambiguation variables
                    self._clear_disambiguation_cache()
                    return (filtered_result, 1)

                # (ii) Cache multiple result options for future disambiguation
                else:
                    filtered_result["response"] += tabstr + f"- all of the above"
                    self._disambiguation_prop_label["prop"] = prop
                    return (filtered_result, 0)

            # (b) SINGLE RESULT LOGIC
            else:
                # return necessary information
                if domain_and_range:
                    filtered_result[
                        "response"
                    ] = f"For property '{property_label}', the domain is '{domain_label}' and range is '{range_label}'."
                elif domain_only:
                    filtered_result[
                        "response"
                    ] = f"For property '{property_label}', the domain is '{domain_label}'."
                elif range_only:
                    filtered_result[
                        "response"
                    ] = f"For property '{property_label}', the range is '{range_label}'."
                return (filtered_result, 1)

        # (3) INVALID DOMAIN/RANGE QUERY
        else:
            filtered_result = self._send_domain_range_error()
            return (filtered_result, 1)


class SubSuperStrategy(NLPStrategy):
    def _send_subsuper_error(self):
        """
        Send back a response message to the user asking them to reformat their sub/super-class query.

        Returns:
            filtered_result: A dictionary of a response
        """
        filtered_result = {}
        filtered_result[
            "response"
        ] = f"Sorry, phrase your query as 'What are the sub/super-classes of __?'"
        return filtered_result

    def execute(self, tagged_tokens, cache, client):
        """
        Processes user queries that ask a basic "sub / super-class" question. In the context of RDF triples, the user
        should prompt a property_label, which will match all property_labels that match the criteria and return their
        associated domain and range entries as labels or uris. Disambiguation occurs for multiple matchine property
        labels. Multi-word property labels must be wrapped in quotes.

        Args:
            tagged_tokens: A list of tokens

        Returns:
            filtered_result: A dict containing a response english string
            status: A boolean for whether query requires disambiguation
        """
        filtered_result = {}

        # extract subclass OR superclass index from tokens
        sub_index = -1
        super_index = -1
        try:
            sub_index = tagged_tokens.index(("subclass", "NN"))
        except ValueError:
            try:
                sub_index = tagged_tokens.index(("subclasses", "VBZ"))
            except ValueError:
                sub_index = -1

        try:
            super_index = tagged_tokens.index(("superclass", "NN"))
        except ValueError:
            try:
                super_index = tagged_tokens.index(("superclasses", "VBZ"))
            except ValueError:
                super_index = -1

        uri_index = sub_index + 1 if sub_index > super_index else super_index + 1

        # Error check tagged_tokens access
        if uri_index >= len(tagged_tokens):
            return (self._send_subsuper_error(), 1)

        # (1) SUBCLASS state
        if (("subclass", "NN") in tagged_tokens) or (
            ("subclasses", "VBZ") in tagged_tokens
        ):
            uri = tagged_tokens[uri_index][0].strip('"')
            result = client.subclass_query(super=uri)
            subclasses = []

            # NO RESULTS
            if len(result) == 0:
                filtered_result[
                    "response"
                ] = f"Unable to find information for subclasses of '{uri}'"
                return (filtered_result, 1)

            # extract subclasses for specified superclass
            for entity in result:
                for key, dic in entity.items():
                    if key == "sub":
                        subclasses.append(dic["value"])

            # create response object with all subclasses
            collected_response = f"The subclasses for '{uri}' are:<br>"

            tabstr = "&nbsp;" * 4
            for sub in subclasses[:-1]:
                collected_response += tabstr + f"- {sub} <br> "
            collected_response += (
                "" if len(subclasses) < 1 else tabstr + f"- {subclasses[-1]} <br> "
            )

            filtered_result["response"] = collected_response
            return (filtered_result, 1)

        # (2) SUPERCLASS state
        elif (("superclass", "NN") in tagged_tokens) or (
            ("superclasses", "VBZ") in tagged_tokens
        ):
            uri = tagged_tokens[uri_index][0].strip('"')
            result = client.superclass_query(sub=uri)
            superclasses = []

            # NO RESULTS
            if len(result) == 0:
                filtered_result[
                    "response"
                ] = f"Unable to find information for superclasses of '{uri}'"
                return (filtered_result, 1)

            # extract superclasses for specified subclass
            for entity in result:
                for key, dic in entity.items():
                    if key == "super":
                        superclasses.append(dic["value"])

            # create response object with all subclasses
            collected_response = f"The superclasses for '{uri}' are:<br>"

            tabstr = "&nbsp;" * 4
            for super in superclasses[:-1]:
                collected_response += tabstr + f"- {super} <br> "
            collected_response += (
                "" if len(superclasses) < 1 else tabstr + f"- {superclasses[-1]} <br> "
            )

            filtered_result["response"] = collected_response
            return (filtered_result, 1)
        # (3) POORLY FORMATTED QUERY
        else:
            return (self._send_subsuper_error(), 1)


class AssemblyStrategy(NLPStrategy):
    def _processURI(self, uri: str):
        """
        Convert a URI that represents the function of an assembly object into NL
        """
        _, func = uri.split("#")
        func_str = re.findall("[A-Z][^A-Z]*", func)
        func_str = [
            func_str[i] if i == 0 else func_str[i].lower() for i in range(len(func_str))
        ]
        return " ".join(func_str)

    def execute(self, tagged_tokens, cache, client):
        """
        Assembly query handles the quesition related to the "mass / function" of a particular assembly object.
        Users should provide an assembly object with "id" specified, associated mass (int) or function (list)
        will be returned depending on the question asked.

        Args:
            tagged_tokens: A list of tokens

        Returns:
            filtered_result: A dict containing a response english string
            status: A boolean for whether query requires disambiguation
        """

        filtered_result = {}
        result_dict = defaultdict(list)

        if ("id", "NN") not in tagged_tokens:
            filtered_result[
                "response"
            ] = "Please ask the question again and contain the keyword 'id' in your question :)"
            return (filtered_result, 1)

        id_index = tagged_tokens.index(("id", "NN"))
        id = tagged_tokens[id_index + 1][0]
        results = client.assembly_query(id=str(id))

        if len(results) == 0:
            filtered_result[
                "response"
            ] = f"Unable to find information about assembly object id {id}"
            return (filtered_result, 1)

        filtered_result["response"] = f"For assembly object {id}: <br>\n "

        for result in results:
            for k, v in result.items():
                if ("mass", "NN") in tagged_tokens and k == "mass":
                    if "mass" not in result_dict:
                        result_dict["mass"].append(v["value"])
                        filtered_result[
                            "response"
                        ] += f"The mass is {float(v['value'])} kg. <br>\n "
                if ("function", "NN") in tagged_tokens and k == "function":
                    if v["value"] in result_dict["function"]:
                        continue
                    result_dict["function"].append(v["value"])

        if "function" in result_dict:
            result_dict["function"] = [
                self._processURI(uri) for uri in result_dict["function"]
            ]

            if len(result_dict["function"]) == 1:
                filtered_result["response"] += f"The function is: <br> "
            else:
                filtered_result["response"] += f"The functions are: <br> "

            tabstr = "&nbsp;" * 4
            for func in result_dict["function"]:
                filtered_result["response"] += tabstr + f"- {func} <br> "
        return (filtered_result, 1)


class Strategy(Enum):
    NONE = 0
    WHAT = 1
    DOMAIN_RANGE = 2
    DOMAIN_RANGE_PROPERTY = 3
    ASSEMBLY = 4
    SUBSUPER = 5


class NaturalLanguageQueryExecutor:
    def __init__(self, client):
        self.client = client
        self.predicate_cache = dict()
        self._query_cache = dict()
        self._strategy_state = Strategy.NONE

    def query(self, query: Query):
        query.set_client(self.client)
        query.set_cache(self.predicate_cache)

        # only parse input if not disambiguating
        if self._strategy_state == Strategy.NONE:
            query.set_tokens(self._parse(query.user_input))
        else:
            query.set_tokens([query.user_input.strip()])

        # set query strategy
        # 1) DOMAIN_RANGE_PROPERTY
        if (self._strategy_state == Strategy.DOMAIN_RANGE_PROPERTY) or (
            (("property", "NN") in query.tokens)
            or (("properties", "NNS") in query.tokens)
        ):
            query.set_strategy(DomainRangePropertyStrategy())
            self._strategy_state = Strategy.DOMAIN_RANGE_PROPERTY
        # 2) DOMAIN_RANGE
        elif (self._strategy_state == Strategy.DOMAIN_RANGE) or (
            (("domain", "NN") in query.tokens) or (("range", "NN") in query.tokens)
        ):
            query.set_strategy(DomainRangeStrategy())
            self._strategy_state = Strategy.DOMAIN_RANGE
        # 3) ASSEMBLY
        elif (("mass", "NN") in query.tokens) or (("function", "NN") in query.tokens):
            query.set_strategy(AssemblyStrategy())
            self._strategy_state = Strategy.ASSEMBLY
        # 4) SUBSUPER
        elif (
            (("subclass", "NN") in query.tokens)
            or (("subclasses", "VBZ") in query.tokens)
            or (("superclass", "NN") in query.tokens)
            or (("superclasses", "VBZ") in query.tokens)
        ):
            query.set_strategy(SubSuperStrategy())
            self._strategy_state = Strategy.SUBSUPER
        # 5) WHAT
        elif (self._strategy_state == Strategy.WHAT) or (
            query.tokens[0][0] == "What" and len(query.tokens) >= 3
        ):
            query.set_strategy(WhatStrategy())
            self._strategy_state = Strategy.WHAT

        return self.process_query(query)

    def process_query(self, query: Query):
        if len(query.tokens) > 2:
            # Identifying subject and predicate
            subject = query.tokens[1][
                0
            ]  # subject: analysis, base, bundle, mission, project, etc
            predicate = query.tokens[2][0]  # predicate: imports, description, etc

            # Checking if previous query was made already
            if (subject, predicate) in self._query_cache:
                return self._query_cache[(subject, predicate)]

        # Use status to enforce continued query for disambiguation
        result, status = query.execute()

        if status:
            self._strategy_state = Strategy.NONE

        return result

    def _parse(self, text: str) -> list:
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
        # Replace all urls with "unique" string
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        urls = re.findall(regex, text)
        text_spaced = text.strip().split(" ")
        replacements = dict()
        for i, t in enumerate(text_spaced):
            if bool(re.match(regex, t)):
                unique_string = f"SUPER_SPECIAL_UNIQUE_URL{i}"
                replacements[unique_string] = text_spaced[i]
                text_spaced[i] = unique_string

        # Replace quoted string with "quotation" string
        unique_string = None
        quote_token = ""
        in_quote = False
        quote_counter = 0
        for i, t in enumerate(text_spaced):
            # single-word quote case
            if t[0] == '"' and (t[-1] == '"' or t[-2] == '"'):
                unique_string = f"QUOTATION{i}"
                replacements[unique_string] = t
                text_spaced[int(unique_string[-1])] = unique_string
                quote_counter += 1
            # multi-word quote case
            elif t[0] == '"':
                unique_string = f"QUOTATION{i}"
                quote_token += t + " "
                in_quote = True
                quote_counter += 1
            elif in_quote and (t[-1] == '"' or t[-2] == '"'):
                quote_token += t
                replacements[unique_string] = quote_token
                text_spaced[int(unique_string[-1])] = unique_string
                in_quote = False
            elif in_quote:
                quote_token += t + " "
                quote_counter += 1

        if quote_token:
            text_spaced = text_spaced[:-quote_counter]
        text = " ".join(text_spaced)

        # Tokenize user query
        tokens = nltk.word_tokenize(text)

        # Replace placeholders with original links
        for i, token in enumerate(tokens):
            if token in replacements and token.startswith("QUOTATION"):
                tokens[i] = f'{replacements[token].strip("?,.")}'
            elif token in replacements:
                tokens[i] = f"<{replacements[token]}>"

        # Filter redundant words
        stop_words = stopwords.words("english")
        filtered_tokens = [t for t in tokens if t not in stop_words]
        # Tag parse
        tagged_tokens = nltk.pos_tag(filtered_tokens)
        return tagged_tokens
