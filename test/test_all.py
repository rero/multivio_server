#T!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test all the modules
"""

#==============================================================================
#  This file is part of the Multivio software.
#  Project  : Multivio - https://www.multivio.org/
#  Copyright: (c) 2009-2011 RERO (http://www.rero.ch/)
#  License  : See file COPYING
#==============================================================================

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
import test_processor

# create a big test suite
test_suite = (
    unittest.makeSuite (test_parser.PdfParserOK),
    unittest.makeSuite (test_parser.DublinCoreParserOK),
    unittest.makeSuite (test_parser.MetsParserOK),
    unittest.makeSuite (test_parser.MarcParserOK),
    unittest.makeSuite (test_logger.LoggerOK),
    unittest.makeSuite (test_processor.PdfProcessorOK),
    )

# create the runner for the tests
runner = unittest.TextTestRunner ()

# run all the tests
runner.run (unittest.TestSuite (test_suite))
