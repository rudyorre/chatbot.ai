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


class TryTestingDomainRangeProperty(TestCase):
    def test_domain_range_property_domain_query_foundation(self):
        tests = {
            "What are the properties of domain Authority?": "For domain 'Authority', the properties are: authorizes, executes, produces, relies on, supplies.",
            "What are the properties of domain QuantityValue?": "For domain 'QuantityValue', the properties are: isAttributedTo, isReferenceValue, isTrueValue.",
            "What are the properties of domain Explanation?": "For domain 'Explanation', the properties are: analyzes, explains, validates.",
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_domain_range_property_domain_query_multi_word_property(self):
        tests = {
            'What are the properties of domain "Quantity Value Constraint"?': "For domain 'Quantity Value Constraint', the properties are: has quantity value, has quantity value relation.",
            'What are the properties of domain "Developed Element"': "For domain 'Developed Element', the properties are: manifests.",
            'What are the properties of domain "Requirement"?': "For domain 'Requirement', the properties are: applies during, forbids, requires, has rationale, refines, specifies.",
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_domain_range_property_range_query_foundation(self):
        tests = {
            "What are the properties of range Authority?": "For range 'Authority', the properties are: authorizes, has responsibility for.",
            "What are the properties of range QuantityValue?": "For range 'QuantityValue', the properties are: yieldsMeasuredValue, has quantity value.",
            "What are the properties of range Component?": "For range 'Component', the properties are: deploys, influences.",
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_domain_range_property_range_query_multi_word_property(self):
        tests = {
            "What are the properties of range Robot?": "Unable to find information about range Robot",
            'What are the properties of range "Deliverable"': "For range 'Deliverable', the properties are: delivers, has participant, receives.",
            "What is the property of range Junction?": "For range 'Junction', the properties are: traverses.",
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_domain_range_query_error(self):
        tests = {
            "What is the property of domain Robot": "Unable to find information about domain Robot",
            "What are the properties of range Car?": "Unable to find information about range Car",
            'What are the properties of domain "Summarized Element"?': "Unable to find information about domain Summarized Element",
        }
        for query, output in tests.items():
            assert check_query(query, output)
