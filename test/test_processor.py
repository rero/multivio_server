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

# local modules
import multivio

from multivio.pdf_processor import PdfProcessor

# add the current path to the python path, so we can execute this test
# from any place
sys.path.append (os.getcwd ())
pdf_file_name = 'examples/document.pdf'

class PdfProcessorOK (unittest.TestCase):
    """
    Test DocumentParser Class.
    """

    def testPdfProcessor(self):
        """Check PdfProcessor instance."""
        pdf_processor = PdfProcessor(pdf_file_name)
        self.assert_ (pdf_processor, "Can not create simple Parser Object")
    
    def testPdfProcess(self):
        """Check Page extraction."""
        pdf_processor = PdfProcessor(pdf_file_name)
        (mime, content)  = pdf_processor.render(index={'page_number':1},
        max_output_size = (100,100))
        print mime
    

if __name__ == '__main__':
    # the main program if we execute directly this module

    # do all the tests
    unittest.main()
