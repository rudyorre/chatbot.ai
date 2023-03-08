from unittest import TestCase
import os
import requests


def check_query(query, output):
    ENDPOINT = "http://localhost:8080"
    HEADERS = {"Content-Type": "application/json"}
    # Make POST request
    requests.post(url=f"{ENDPOINT}/query", headers=HEADERS, json={"data": query})
    # Make GET request
    response = requests.get(url=f"{ENDPOINT}/response").json()["response"]
    return response == output


class TryTestingDomainRange(TestCase):
    def test_domain_range_query_foundation(self):
        tests = {
            "What is the domain and range of isCoherent?": "For property 'isCoherent', the domain is 'HasCoherence' and range is 'http://www.w3.org/2001/XMLSchema#boolean'.",
            "What is the domain and range of hasDoubleNumber?": "For property 'hasDoubleNumber', the domain is 'UnitaryQuantityValue' and range is 'http://www.w3.org/2001/XMLSchema#double'.",
            "What is the domain and range of delivers?": "For property 'delivers', the domain is 'Interchange Point' and range is 'Deliverable'.",
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_domain_range_query_multi_word_property(self):
        tests = {
            'What is the domain and range of "system has derived unitary quantity"?': "For property 'system has derived unitary quantity', the domain is 'system of quantities' and range is 'general unitary quantity'.",
            'What is the domain and range of "is required not later than"?': "For property 'is required not later than', the domain is 'Deliverable' and range is 'http://www.w3.org/2001/XMLSchema#dateTime'.",
            'What is the domain and range of "has assignment"?': "For property 'has assignment', the domain is 'Role' and range is 'Assigned Element'.",
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_domain_range_query_single_domain(self):
        tests = {
            'What is the domain of "system has derived unitary quantity"?': "For property 'system has derived unitary quantity', the domain is 'system of quantities'.",
            'What is the domain of "is required not later than"?': "For property 'is required not later than', the domain is 'Deliverable'.",
            'What is the domain of "has assignment"?': "For property 'has assignment', the domain is 'Role'.",
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_domain_range_query_single_range(self):
        tests = {
            'What is the range of "system has derived unitary quantity"?': "For property 'system has derived unitary quantity', the range is 'general unitary quantity'.",
            'What is the range of "is required not later than"?': "For property 'is required not later than', the range is 'http://www.w3.org/2001/XMLSchema#dateTime'.",
            'What is the range of "has assignment"?': "For property 'has assignment', the range is 'Assigned Element'.",
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_domain_range_query_error(self):
        tests = {
            "What is the domain and range of sdf?": "Unable to find information for domain/range of 'sdf'",
            'What is the domain and range of "has actual assignment"?': "Unable to find information for domain/range of 'has actual assignment'",
            'What is the domain and range of "represent"?': "Unable to find information for domain/range of 'represent'",
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_domain_range_query_disambiguation(self):
        tests = {
            "What is the domain and range of describes?": "For property 'describes', which data source are you referring to: <br>&nbsp;&nbsp;&nbsp;&nbsp;- bipm.org/jcgm/vim4 <br>&nbsp;&nbsp;&nbsp;&nbsp;- imce.jpl.nasa.gov/foundation/project <br>&nbsp;&nbsp;&nbsp;&nbsp;- all of the above",
            "all of the above": "For property 'describes' in bipm.org/jcgm/vim4, the domain is 'MeasurementProcedure' and range is 'Measurement'. For property 'describes' in imce.jpl.nasa.gov/foundation/project, the domain is 'Product' and range is 'Developed Element'. ",
            'What is the domain and range of "transfers in"?': "For property 'transfers in', the domain is 'Interface' and range is 'Presenting Element'. For property 'transfers in', the domain is 'Interface' and range is 'Traversing Element'. ",
            'What is the domain and range of "invokes"?': "For property 'invokes', which data source are you referring to: <br>&nbsp;&nbsp;&nbsp;&nbsp;- imce.jpl.nasa.gov/foundation/mission <br>&nbsp;&nbsp;&nbsp;&nbsp;- imce.jpl.nasa.gov/foundation/project <br>&nbsp;&nbsp;&nbsp;&nbsp;- all of the above",
            "imce.jpl.nasa.gov/foundation/project": "For property 'invokes' in imce.jpl.nasa.gov/foundation/project, the domain is 'Process' and range is 'Process'.",
        }
        for query, output in tests.items():
            assert check_query(query, output)
