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
        self.soup = BeautifulSoup(self.getdocument(),"xsd")

    def test_select(self):
        selectsoup = self.soup.select("complexType");
        for select in selectsoup:
            #print(select.contents[1])
            print("content")
    def test_complextype(self):
        print("complextype")
        print(self.soup.parse_xsd("complexType", etree,self.getdocument()))
    def test_simpletype(self):
        print("simpletype")
    def getdocument(self):
        return open("xsd.txt")

if __name__ == '__main__':
    unittest.main()






    
