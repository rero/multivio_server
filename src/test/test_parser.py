#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit test for the verif scores module.

This file is part of the pyMeasure scripts module.
"""

# some general value for this module
__author__ = "Johnny Mariethoz <Johnny.Mariethoz@idiap.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"

# standard modules
import sys
import os
import unittest
import ConfigParser
import json

# local modules
import multivio

# add the current path to the python path, so we can execute this test
# from any place
sys.path.append (os.getcwd ())

mods_file_name = 'test/test.mods'
marc_file_name = 'test/test.marc'
dc_file_name = 'test/test.xd'

class ParserOK (unittest.TestCase):
    """
    Test Parser Class.
    """

    def testParser(self):
        """Check logger instance."""
        parser = multivio.parser.ParserSelector()
        self.assert_ (parser, "Can not create simple Parser Object")
    
#    def testMarcParser(self):
#        """Check a Marc parser."""
#        parser = multivio.parser.ParserSelector()
#        marc = parser.parseFile(marc_file_name)
#        marc.display()
#        
#    
#    def testModsParser(self):
#        """Check a Mods parser."""
#        parser = multivio.parser.ParserSelector()
#        mods = parser.parseFile(mods_file_name)
#        mods.display()
    
    def testDcParser(self):
        """Check a Dublin Core parser."""
        parser = multivio.parser.ParserSelector()
        mods = parser.parseFile(dc_file_name)
        mods.display()
    
    def tearDown(self):
        pass
        

if __name__ == '__main__':
    # the main program if we execute directly this module

    # do all the tests
    unittest.main()
