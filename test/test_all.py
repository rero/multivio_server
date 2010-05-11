#T!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test all the modules
"""
# some general value for this module
__author__ = "Johnny Mariethoz <Johnny.Mariethoz@idiap.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"

# some usefull modules
import sys
import os

# the standard classes for making the tests
import unittest

# add the current path to the python path, so we can execute this test
# from any place, and it can find all the other tests
sys.path.append (os.getcwd ())

# import all the specific test modules
import test_logger
import test_parser

# create a big test suite
test_suite = (
    unittest.makeSuite (test_parser.PdfParserOK),
    unittest.makeSuite (test_parser.DublinCoreParserOK),
    unittest.makeSuite (test_parser.MetsParserOK),
    unittest.makeSuite (test_parser.MarcParserOK),
    unittest.makeSuite (test_logger.LoggerOK),
    )

# create the runner for the tests
runner = unittest.TextTestRunner ()

# run all the tests
runner.run (unittest.TestSuite (test_suite))
