from unittest import TestCase
import os
import requests


def check_query(query, output):
    ENDPOINT = "http://localhost:8080"
    HEADERS = {"Content-Type": "application/json"}
    # Make POST request
    requests.post(url=f"{ENDPOINT}/query",
                  headers=HEADERS, json={"data": query})
    # Make GET request
    response = requests.get(url=f"{ENDPOINT}/response").json()["response"]
    return response == output


class TryTestingAssembly(TestCase):
    def test_assembly_foundation(self):
        tests = {
            "What is the mass and function of assembly object id 500000?": "For assembly object 500000: <br>\n The mass is 0.6 kg. <br>\n The functions are: <br> &nbsp;&nbsp;&nbsp;&nbsp;- Perform mission by spacecraft system segment <br> &nbsp;&nbsp;&nbsp;&nbsp;- Detect new wildfires by spacecraft system segment <br> &nbsp;&nbsp;&nbsp;&nbsp;- Monitor existing wildfires_24_7 by spacecraft system segment <br> ",
            "What is the mass of assembly object id 500000?": "For assembly object 500000: <br>\n The mass is 0.6 kg. <br>\n ",
            "What is the function of assembly object id 500000?": "For assembly object 500000: <br>\n The functions are: <br> &nbsp;&nbsp;&nbsp;&nbsp;- Perform mission by spacecraft system segment <br> &nbsp;&nbsp;&nbsp;&nbsp;- Detect new wildfires by spacecraft system segment <br> &nbsp;&nbsp;&nbsp;&nbsp;- Monitor existing wildfires_24_7 by spacecraft system segment <br> "
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_assembly_error(self):
        tests = {
            "What is the mass and function of assembly object id 51600?": "Unable to find information about assembly object id 51600",
            "What is the mass of assembly object id 51600?": "Unable to find information about assembly object id 51600",
            "What is the function of assembly object id 51600?": "Unable to find information about assembly object id 51600",
            "What is the mass of assembly object 51600?": "Please ask the question again and contain the keyword 'id' in your question :)"
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_assembly_filter(self):
        tests = {
            "Which subjects are heavier than 0.8 kg and lighter than 2 kg?": "The subjects are: <br> &nbsp;&nbsp;&nbsp;&nbsp;- Primary thruster <br> &nbsp;&nbsp;&nbsp;&nbsp;- Propulsion system control unit <br> &nbsp;&nbsp;&nbsp;&nbsp;- Base plate <br> &nbsp;&nbsp;&nbsp;&nbsp;- GPS receiver unit <br> &nbsp;&nbsp;&nbsp;&nbsp;- Magnetometer <br> &nbsp;&nbsp;&nbsp;&nbsp;- Receiver unit <br> ",
            "Which subjects are heavier than 10 kg?": "The subjects are: <br> &nbsp;&nbsp;&nbsp;&nbsp;- Propellant tank <br> &nbsp;&nbsp;&nbsp;&nbsp;- EPS regulators and converters unit <br> &nbsp;&nbsp;&nbsp;&nbsp;- Sensor <br> ",
            "Which subjects are lighter than 0.1 kg?": "The subjects are: <br> &nbsp;&nbsp;&nbsp;&nbsp;- Receive whip antenna <br> &nbsp;&nbsp;&nbsp;&nbsp;- Transmit hi gain antenna <br> &nbsp;&nbsp;&nbsp;&nbsp;- Transmit whip antenna <br> "
        }
        for query, output in tests.items():
            assert check_query(query, output)

    def test_assembly_filter_error(self):
        tests = {
            "Which subjects are heavier than 50 kg and lighter than 1 kg?": "Please enter a valid mass range",
            "Which subjects are heavier than 50 kg?": "Unable to find information for subjects within this range"
        }
        for query, output in tests.items():
            assert check_query(query, output)
