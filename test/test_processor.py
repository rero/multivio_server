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
    Test PdfProcessor Class.
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

    def testPdfGetText(self):
        """Check text extraction"""
        pdf_processor = PdfProcessor(pdf_file_name)
        result = pdf_processor.get_text(index={'page_number':1, 'bounding_box':{'x1':147,'x2':239,'y1':260,'y2':277}})
        self.assertEqual(result.has_key('text'), True)
        self.assertEqual(result['text'], u'Introduction')

    def testPdfGetPageIndexing(self):
        """Check page indexing"""
        pdf_processor = PdfProcessor(pdf_file_name)
        result = pdf_processor.get_indexing(index={'page_number':2})
        self.assertEqual(result.has_key('pages'), True)
        self.assertEqual(len(result['pages']), 1)
        self.assertEqual(result['pages'][0].has_key('lines'), True)
        self.assertEqual(len(result['pages'][0]['lines']), 39) # number of lines on page
        self.assertEqual(len(result['pages'][0]['lines'][0]['x']), 13) # number of words on page

    def testPdfSearch(self):
        """Check regular search"""
        pdf_processor = PdfProcessor(pdf_file_name)
        result = pdf_processor.search(query='multivio', context_size=12)
        self.assertEqual(result.has_key('file_position'), True)
        self.assertEqual(len(result['file_position']['results']), 9) # number of search results
        first_result = result['file_position']['results'][0]['index']['bounding_box']
        self.assertAlmostEqual(first_result['x1'], 196)
        self.assertAlmostEqual(first_result['y1'], 166)
        self.assertAlmostEqual(first_result['x2'], 255)
        self.assertAlmostEqual(first_result['y2'], 181)
        # checking context preview. It should contain the searched term 'multivio'
        first_result = result['file_position']['results'][0]
        self.assertNotEqual(first_result['preview'].lower().find('multivio'), -1)

    def testPdfSearchNoResult(self):
        """Check search when there's no result"""
        pdf_processor = PdfProcessor(pdf_file_name)
        result = pdf_processor.search(query='camembert')
        self.assertEqual(result['max_reached'], 0)
        self.assertEqual(len(result['file_position']['results']), 0) # number of search results

    def testPdfSearchMaxNumberOfResults(self):
        """Check search with a limit on the number of search results"""
        pdf_processor = PdfProcessor(pdf_file_name)
        result = pdf_processor.search(query='e', max_results=1)
        self.assertEqual(result['max_reached'], 1)
        self.assertEqual(len(result['file_position']['results']), 1) # number of search results

        result = pdf_processor.search(query='e', max_results=14)
        self.assertEqual(result['max_reached'], 14)
        self.assertEqual(len(result['file_position']['results']), 14) # number of search results

        result = pdf_processor.search(query='e', max_results=88)
        self.assertEqual(result['max_reached'], 88)
        self.assertEqual(len(result['file_position']['results']), 88) # number of search results

    def testPdfSearchRotation(self):
        """Check search results and context with different rotation angles"""
        pdf_processor = PdfProcessor(pdf_file_name)
        result1 = pdf_processor.search(query='user', angle=  0, context_size=15)
        result2 = pdf_processor.search(query='user', angle= 90, context_size=15)
        result3 = pdf_processor.search(query='user', angle=180, context_size=15)
        result4 = pdf_processor.search(query='user', angle=270, context_size=15)

        # number of results should always be the same
        n1 = len(result1['file_position']['results'])
        n2 = len(result2['file_position']['results'])
        n3 = len(result3['file_position']['results'])
        n4 = len(result4['file_position']['results'])

        # context preview should be the same everywhere
        c1 = result1['file_position']['results'][0]['preview']
        c2 = result2['file_position']['results'][0]['preview'] 
        c3 = result3['file_position']['results'][0]['preview'] 
        c4 = result4['file_position']['results'][0]['preview'] 

        self.assertEqual(n1, n2)
        self.assertEqual(n2, n3) 
        self.assertEqual(n3, n4) 
        self.assertEqual(c1, c2) 
        self.assertEqual(c2, c3) 
        self.assertEqual(c3, c4) 

if __name__ == '__main__':
    # the main program if we execute directly this module

    # do all the tests
    unittest.main()
