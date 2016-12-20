'''
Created on Nov 20, 2016

@author: Technia
'''

from bs4 import BeautifulSoup
from lxml import etree
import unittest
from types import DictionaryType


class XSDParsing(unittest.TestCase):
    '''
    classdocs
    '''
     
    def setUp(self):
        self.soup = BeautifulSoup(self.getdocument(),"xsd")
        self.values = self.soup.parse_xsd(etree,self.getdocument())

    def test_complextype(self):
        names = self.get_name(self.values, "complexType")
        
        self.assertEqual(names[0], "simpleAddressType", "Checking for 1st values")
        self.assertEqual(names[1], "certified", "Checking for 2nd values")
        self.assertEqual(names[2], "testing", "Checking for 3rd values")
        self.assertIn("certified", names, "Test for 2nd value")
        self.assertIsNotNone(names, "Parsed value is not None")
        self.assertNotIn("Christmas", names, "Check for containing")
        self.assertNotEqual("certificationEnum", names[1], "Check for values")
        self.assertIsInstance(names, list, "instance of Arrays")
        self.assertIsInstance(self.values, DictionaryType, "instance of dictionary")
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
        self.assertEqual(names[0], "certificationEnum", "Checking for 1st values")
        self.assertEqual(names[1], "yesNoEnum", "Checking for 2nd values")
        self.assertIn("yesNoEnum", names, "Test for 2nd value")
        self.assertIsInstance(names, list, "instance of Arrays")
        self.assertGreaterEqual(4, len(names), "check for equal size")
        self.assertGreater(10, len(names), "check for size")
        self.assertNotIsInstance(names, DictionaryType, "Check for instance")
        
    def get_name(self, values, argument):
        names = []
        for t in values[argument]:
            names.append(t["name"])
        return names
    
    def get_elements(self, values, argument):
        names = []
        for t in values[argument]:
            try:
                elements= t["elements"]
                for e in elements:
                    names.append(e["name"])
            except KeyError:
                pass
            
        return names
    
    def get_type(self, values, argument):
        names = []
        for t in values[argument]:
            try:
                elements= t["elements"]
                for e in elements:
                    names.append(e["type"])
            except KeyError:
                pass
            
        return names
        
    def getdocument(self):
        return open("xsd.txt")

if __name__ == '__main__':
    unittest.main()






    
