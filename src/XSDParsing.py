'''
Created on Nov 20, 2016

@author: Technia
'''
from lxml import etree
import unittest
from types import DictionaryType
from StringIO import StringIO
# add the local repo to python path with top priority, otherwise python might
# use bs4 as it is installed on the system.
import sys
sys.path.insert(0, '../library/')
from bs4 import BeautifulSoup


class XSDParsing(unittest.TestCase):

    def setUp(self):
        self.soup = BeautifulSoup(self.getdocument(), "xsd")
        self.values = self.soup.parse_xsd(etree, self.getdocument())
        self.simplest_xsd = '<?xml version="1.0" encoding="UTF-8" ?>' \
            '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
            '</xs:schema>'
        self.incomplete_xsd = '<?xml version="1.0" encoding="UTF-8" ?>' \
            '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
            '<xs:element name="note">' \
            '</xs:schema>'

    def test_complextype(self):
        names = self.get_name(self.values, "complexType")

        self.assertEqual(names[0], "simpleAddressType",
                         "Checking for 1st values")
        self.assertEqual(names[1], "certified", "Checking for 2nd values")
        self.assertEqual(names[2], "testing", "Checking for 3rd values")
        self.assertIn("certified", names, "Test for 2nd value")
        self.assertIsNotNone(names, "Parsed value is not None")
        self.assertNotIn("Christmas", names, "Check for containing")
        self.assertNotEqual("certificationEnum", names[1], "Check for values")
        self.assertIsInstance(names, list, "instance of Arrays")
        self.assertIsInstance(self.values, DictionaryType,
                              "instance of dictionary")
        self.assertGreater(25, len(names), "Check for size")
        self.assertTrue(len(names) > 2, "Test for condition")

        elements = self.get_elements(self.values, "complexType")
        self.assertEqual("line1", elements[1], "Check for 2nd element")
        self.assertEqual("line2", elements[2], "Check for 3rd element")
        self.assertEqual("line3", elements[3], "Check for 4th element")
        self.assertIn("state", elements, "check for content")
        self.assertIn("city", elements, "check for content")
        self.assertIn("zip", elements, "check for content")
        self.assertIsNotNone(elements, "Check for elements")
        self.assertGreater(20, len(elements), "Check for size")
        self.assertLess(2, len(elements), "check for size")
        self.assertNotEquals("liness", elements[2], "Check for content")
        self.assertNotEquals("state", elements[0], "Check for content")

        types = self.get_type(self.values, "complexType")
        self.assertIn("xs:string", types, "Check for content")
        self.assertIn("xs:integer", types, "Check for content")
        self.assertNotIn("xs:date", types, "Check for content")
        self.assertLess(1, len(types), "check for size")
        self.assertTrue(len(types) > 2, "Test for condition")

    def test_simpletype(self):
        names = self.get_name(self.values, "simpleType")
        self.assertEqual(names[0], "certificationEnum",
                         "Checking for 1st values")
        self.assertEqual(names[1], "yesNoEnum", "Checking for 2nd values")
        self.assertIn("yesNoEnum", names, "Test for 2nd value")
        self.assertIsInstance(names, list, "instance of Arrays")
        self.assertGreaterEqual(4, len(names), "check for equal size")
        self.assertGreater(10, len(names), "check for size")
        self.assertNotIsInstance(names, DictionaryType, "Check for instance")

    def test_parse_xsd(self):
        ve1 = False
        try:
            self.soup.parse_xsd()
        except ValueError:
            ve1 = True
        except:
            pass
        self.assertTrue(ve1, "no etreeobject argument")

        ve2 = False
        try:
            self.soup.parse_xsd(etreeobject=etree)
        except ValueError:
            ve2 = True
        except:
            pass
        self.assertTrue(ve2, "no document argument")

        ioe = False
        try:
            self.soup.parse_xsd(etree, StringIO(self.incomplete_xsd))
        except etree.XMLSyntaxError:
            ioe = True
        except:
            pass
        self.assertTrue(ioe, "incomplete syntax")

    def test_select_xsd(self):
        soup = BeautifulSoup(self.simplest_xsd, "xsd")
        selected_schema = soup.select_xsd("schema")
        self.assertEqual(
            str(selected_schema),
            '[<xs:schema xsd:xs="http://www.w3.org/2001/XMLSchema"/>]',
            "try a simple select")

        selected = self.soup.select_xsd("schema")
        self.assertEqual(len(selected), 1, "one schema occurred")
        for s in selected:
            self.assertEqual(s.name, "schema")

        try:
            selected = selected[0].select_xsd("element")
        except KeyError:
            pass
        self.assertEqual(len(selected), 38, "38 element occurred")
        for e in selected:
            self.assertEqual(e.name, "element")

        try:
            selected = selected[0].select_xsd("complexType")
        except KeyError:
            pass
        self.assertEqual(len(selected), 10, "10 complexType occurred")
        for ct in selected:
            self.assertEqual(ct.name, "complexType")

        try:
            selected = selected[0].select_xsd("all")
        except KeyError:
            pass
        self.assertEqual(len(selected), 4, "4 all occurred")
        for a in selected:
            self.assertEqual(a.name, "all")

        try:
            selected = selected[0].select_xsd("element")
        except KeyError:
            pass
        self.assertEqual(len(selected), 3, "3 element occurred")
        for e in selected:
            self.assertEqual(e.name, "element")

    def test_select_one_xsd(self):
        soup = BeautifulSoup(self.simplest_xsd, "xsd")
        self.assertEqual(
            str(soup.select_one_xsd("schema")),
            '<xs:schema xsd:xs="http://www.w3.org/2001/XMLSchema"/>',
            "try a simple select")

        selected = self.soup.select_one_xsd("schema")
        self.assertEqual(selected.name, "schema", "selected name is schema")
        selected = selected.select_one_xsd("element")
        self.assertEqual(selected.name, "element", "selected name is element")
        selected = selected.select_one_xsd("complexType")
        self.assertEqual(selected.name, "complexType",
                         "selected name is complexType")
        selected = selected.select_one_xsd("all")
        self.assertEqual(selected.name, "all", "selected name is all")
        selected = selected.select_one_xsd("element")
        self.assertEqual(selected.name, "element", "selected name is element")

    # Convenience functions
    def get_name(self, values, argument):
        names = []
        for t in values[argument]:
            names.append(t["name"])
        return names

    def get_elements(self, values, argument):
        names = []
        for t in values[argument]:
            try:
                elements = t["elements"]
                for e in elements:
                    names.append(e["name"])
            except KeyError:
                pass
        return names

    def get_type(self, values, argument):
        names = []
        for t in values[argument]:
            try:
                elements = t["elements"]
                for e in elements:
                    names.append(e["type"])
            except KeyError:
                pass
        return names

    def getdocument(self):
        return open("xsd.txt")


if __name__ == '__main__':
    unittest.main()
