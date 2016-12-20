'''
Created on Nov 20, 2016

@author: Technia
'''

from bs4 import BeautifulSoup
from lxml import etree
import unittest


class XSDParsing(unittest.TestCase):
    '''
    classdocs
    '''
     
    def setUp(self):
        self.xsdfile = open("xsd.txt")
        self.soup = BeautifulSoup(self.xsdfile,"xsd")

    def test_select(self):
        selectsoup = self.soup.select("complexType");
        for select in selectsoup:
            print(select.contents[1])

if __name__ == '__main__':
    unittest.main()






    
