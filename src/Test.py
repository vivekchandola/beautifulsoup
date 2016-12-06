'''
Created on Dec 6, 2016

@author: Technia
'''
import unittest
from bs4 import BeautifulSoup
from lxml import etree

class Test(unittest.TestCase):


    def testName(self):
        doc = "<table><tr><td>one</td><td>two</td></tr></table>"
        soup = BeautifulSoup(doc,"lxml");
        print(soup)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()