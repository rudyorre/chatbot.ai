from unittest import TestCase
import os
import requests

class TryTesting(TestCase):
    def test_what_query(self):
        tests = {
            'What is the base description?': 'The Base vocabulary defines foundation concepts that are common to multiple specialized ontologies.',
            'What is the analysis description?': 'The Analysis vocabulary defines general concepts and properties for analyses (e.g., trade studies, driving requirements analysis, etc.). It provides a basis for specialization by domain experts.',
            'What is the mission description?': 'The Mission vocabulary defines concepts and properties for describing missions in terms of their objectives, their constituent components, the functions those components perform, and the requirements that specify them.',
        }
        ENDPOINT = 'http://localhost:8080'
        HEADERS = {'Content-Type': 'application/json'}

        for query,actual in tests.items():
            # Make POST request
            requests.post(url=f'{ENDPOINT}/query', headers=HEADERS, json={'data': query})
            # Make GET request
            response = requests.get(url=f'{ENDPOINT}/response').json()['response']
            assert response == actual