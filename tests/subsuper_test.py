from unittest import TestCase
from server.routes import app


def check_query(query, output):
    HEADERS = {"Content-Type": "application/json"}
    # Make POST request
    app.test_client().post("testQuery", headers=HEADERS, json={"data": query})
    # Make GET request
    response = app.test_client().get("testResponse")
    assert response.json["response"].strip() == output.strip()


class TryTestingSubSuper(TestCase):
    def test_subsuper_sub_foundation(self):
        tests = {
            'What are the subclasses of "http://imce.jpl.nasa.gov/foundation/analysis#Characterizes"?': "The subclasses for 'http://imce.jpl.nasa.gov/foundation/analysis#Characterizes' are:<br>&nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#Characterizes <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/analysis#Constrains <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/analysis#Explains <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/analysis#Limits <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/analysis#Validates <br> ",
            'What is the subclass of "http://bipm.org/jcgm/vim4#GeneralProperty"?': "The subclasses for 'http://bipm.org/jcgm/vim4#GeneralProperty' are:<br>&nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#GeneralNominalProperty <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#GeneralOrdinalQuantity <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#GeneralQuantity <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#GeneralUnitaryQuantity <br> ",
            'What are the subclasses of "http://imce.jpl.nasa.gov/foundation/analysis#CharacterizedElement"?': "The subclasses for 'http://imce.jpl.nasa.gov/foundation/analysis#CharacterizedElement' are:<br>&nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#IndividualNominalProperty <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#IndividualOrdinalQuantity <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#IndividualQuantity <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#IndividualUnitaryQuantity <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#InherentOrdinalQuantity <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#InherentUnitaryQuantity <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#InherentUnitaryQuantityValue <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#MeasurementUnit <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#Object <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#OrdinalQuantityValue <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#PrefixedMeasurementUnit <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#QuantityValue <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#UnitaryQuantityValue <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#UnprefixedMeasurementUnit <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/mission#Component <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/mission#Interface <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/mission#Junction <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/mission#Requirement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/project#DevelopedElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/project#Facility <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/project#Product <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/project#WorkPackage <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#Assembly <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#EndCircuit <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#Function <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#MassAllocationConstraint <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#MassConstrainedElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#MassConstraint <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#MassLimitConstraint <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#PowerEndCircuit <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#PowerFunction <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#PowerIn <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#PowerOut <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://opencaesar.io/examples/firesat/disciplines/fse/fse#Subsystem <br> ",
        }
        for query, output in tests.items():
            check_query(query, output)

    def test_subsuper_super_foundation(self):
        tests = {
            'What are the superclasses of "http://imce.jpl.nasa.gov/foundation/analysis#Characterizes"?': "The superclasses for 'http://imce.jpl.nasa.gov/foundation/analysis#Characterizes' are:<br>&nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/mission#SpecifiedElement <br> ",
            'What are the superclasses of "http://bipm.org/jcgm/vim4#GeneralProperty"?': "The superclasses for 'http://bipm.org/jcgm/vim4#GeneralProperty' are:<br>&nbsp;&nbsp;&nbsp;&nbsp;- http://bipm.org/jcgm/vim4#IdentifiedElement <br> ",
            'What is the superclass of "http://imce.jpl.nasa.gov/foundation/mission#Component"?': "The superclasses for 'http://imce.jpl.nasa.gov/foundation/mission#Component' are:<br>&nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/analysis#CharacterizedElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/base#AggregatedElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/base#ContainedElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/base#Container <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/base#IdentifiedElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/mission#PerformingElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/mission#PresentingElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/mission#SpecifiedElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/project#DevelopedElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/project#RealizedElement <br> &nbsp;&nbsp;&nbsp;&nbsp;- http://imce.jpl.nasa.gov/foundation/project#SuppliedElement <br> ",
        }
        for query, output in tests.items():
            check_query(query, output)

    def test_subsuper_sub_foundation_error(self):
        tests = {
            'What are the subclasses of "http://imce.jpl.nasa.gov"?': "Unable to find information for subclasses of 'http://imce.jpl.nasa.gov'",
            'What is the subclass for "https://calendar.google.com/calendar/u/0/r/week"?': "Unable to find information for subclasses of 'https://calendar.google.com/calendar/u/0/r/week'",
            'What are the subclasses for "http://imce.jpl.nasa.gov/foundation/base#IdentifiedElement2x"?': "Unable to find information for subclasses of 'http://imce.jpl.nasa.gov/foundation/base#IdentifiedElement2x'",
        }
        for query, output in tests.items():
            check_query(query, output)

    def test_subsuper_super_foundation_error(self):
        tests = {
            'What are the superclasses of "http://imce.jpl.nasa.gov"?': "Unable to find information for superclasses of 'http://imce.jpl.nasa.gov'",
            'What is the superclasses for "https://calendar.google.com/calendar/u/0/r/week"?': "Unable to find information for superclasses of 'https://calendar.google.com/calendar/u/0/r/week'",
            'What are the superclasses for "http://imce.jpl.nasa.gov/foundation/base#IdentifiedElement2x"?': "Unable to find information for superclasses of 'http://imce.jpl.nasa.gov/foundation/base#IdentifiedElement2x'",
        }
        for query, output in tests.items():
            check_query(query, output)
