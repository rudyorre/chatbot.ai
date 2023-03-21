from unittest import TestCase
from server.routes import app


def check_query(query, output):
    HEADERS = {"Content-Type": "application/json"}
    # Make POST request
    app.test_client().post("testQuery", headers=HEADERS, json={"data": query})
    # Make GET request
    response = app.test_client().get("testResponse")
    assert response.json["response"].strip() == output.strip()


class TryTesting(TestCase):
    def test_what_query_foundation(self):
        tests = {
            "What is the base description?": "The Base vocabulary defines foundation concepts that are common to multiple specialized ontologies.",
            "What is the analysis description?": "The Analysis vocabulary defines general concepts and properties for analyses (e.g., trade studies, driving requirements analysis, etc.). It provides a basis for specialization by domain experts.",
            "What is the mission description?": "The Mission vocabulary defines concepts and properties for describing missions in terms of their objectives, their constituent components, the functions those components perform, and the requirements that specify them.",
        }
        for query, output in tests.items():
            check_query(query, output)

    def test_what_query_uri(self):
        tests = {
            "What is the http://purl.org/dc/elements/1.1 title?": "DC",
            "What is the http://iso.org/iso-80000-1#ISQ7 type?": "http://www.w3.org/2002/07/owl#NamedIndividual",
            "What is the http://iso.org/iso-80000-1#ISQ7 id?": "ISQ7",
            "What is http://imce.jpl.nasa.gov/foundation/base description?": "The Base vocabulary defines foundation concepts that are common to multiple specialized ontologies.",
        }
        for query, output in tests.items():
            check_query(query, output)

    def test_what_query_stemming(self):
        tests = {
            "What is the mission descriptions?": "The Mission vocabulary defines concepts and properties for describing missions in terms of their objectives, their constituent components, the functions those components perform, and the requirements that specify them.",
            "What does mission import?": "http://purl.org/dc/elements/1.1",
            "What does http://opencaesar.io/examples/firesat/programs/earth-science/projects/firesat/workpackages/06/06/subsystems/eps/assemblies#BatteryPack1 present?": "http://opencaesar.io/examples/firesat/programs/earth-science/projects/firesat/workpackages/06/06/subsystems/eps/endcircuits#BatteryPack1PowerIn",
        }
        for query, output in tests.items():
            check_query(query, output)
