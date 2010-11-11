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
from multivio.pdf_parser import PdfParser
from multivio.dc_parser import DublinCoreParser
from multivio.mets_parser import MetsParser
from multivio.marc_parser import MarcParser
from multivio.mods_parser import ModsParser

# add the current path to the python path, so we can execute this test
# from any place
sys.path.append (os.getcwd ())
pdf_file_name = 'examples/document.pdf'
mets_file_name = 'examples/test.mets'
mets_file_name = 'examples/test.mets'
marc_file_name = 'examples/test.marc'
dc_file_name = 'examples/test.xd'
mods_file_name = 'examples/test.mods'

class PdfParserOK (unittest.TestCase):
    """
    Test DocumentParser Class.
    """

    def testPdfParser(self):
        """Check PdfParser instance."""
        pdf_parser = PdfParser(pdf_file_name, "file://%s" %
                        pdf_file_name, pdf_file_name)
        self.assert_ (pdf_parser, "Can not create simple Parser Object")
    
    def testPdfBadParser(self):
        """Check PdfParser instance with a bad file."""
        self.assertRaises(multivio.parser.ParserError.InvalidDocument,
                PdfParser, mets_file_name, "file://%s" %
                mets_file_name, mets_file_name)

    def testPdfParserMeta(self):
        """Get Pdf Metadata."""
        pdf_parser = PdfParser(pdf_file_name, "file://%s" %
                        pdf_file_name, pdf_file_name)
        meta = pdf_parser.get_metadata()
        title = meta['title']
        self.assertEqual(title, u'Multivio: Project description', "Metadata has "\
                        "not been correctly detected %s != %s" % 
                        (title, u'Multivio: Project description'))
    
    def testPdfParserLogical(self):
        """Get Pdf logical structure."""
        pdf_parser = PdfParser(pdf_file_name, "file://%s" %
                        pdf_file_name, pdf_file_name)
        logic = pdf_parser.get_logical_structure()
        first_section = logic[0]['label']
        self.assertEqual (first_section, 'Introduction', "TOC is not well "\
                "detected: %s != %s" %(first_section, 'Introduction')) 

    def testPdfParserPhysical(self):
        """Get Pdf physical structure."""
        url = "file://%s" % pdf_file_name
        pdf_parser = PdfParser(pdf_file_name, url, pdf_file_name)
        phys = pdf_parser.get_physical_structure()
        self.assertEqual(phys[0]['label'], pdf_file_name, "Physical Structure "\
                        "missmatch: %s != %s" % (phys[0]['label'], pdf_file_name))

    def tearDown(self):
        pass
        
class DublinCoreParserOK (unittest.TestCase):
    """
    Test DocumentParser Class.
    """

    def testDcParser(self):
        """Check DublinCoreParser instance."""
        dc_file = file(dc_file_name)
        dc_parser = DublinCoreParser(dc_file, 'http://doc.rero.ch')
        self.assert_ (dc_parser, "Can not create simple DublinCoreParser Object")
    
    def testDcBadParser(self):
        """Check DCParser instance with a bad file."""
        dc_file = file(pdf_file_name)
        self.assertRaises(multivio.parser.ParserError.InvalidDocument,
                DublinCoreParser, dc_file, 'http://doc.rero.ch')

    def testDcParserMeta(self):
        """Get DublinCore Metadata."""
        dc_file = file(dc_file_name)
        dc_parser = DublinCoreParser(dc_file, 'http://doc.rero.ch')
        meta = dc_parser.get_metadata()
        title = meta['title']
        self.assertEqual(title, u'Un super titre fait par Johnny Mariéthoz', "Metadata has "\
                        "not been correctly detected %s != %s" % 
                        (title, u'Un super titre fait par Johnny Mariéthoz'))
    
    def testDcParserLogical(self):
        """Get Dc logical structure."""
        dc_file = file(dc_file_name)
        dc_parser = DublinCoreParser(dc_file, 'http://doc.rero.ch')
        logic = dc_parser.get_logical_structure()
        self.assertEqual (logic, None)

    def testDcParserPhysical(self):
        """Get Dc physical structure."""
        dc_file = file(dc_file_name)
        dc_parser = DublinCoreParser(dc_file, 'http://doc.rero.ch')
        phys = dc_parser.get_physical_structure()
        desired_out =  u"Bartholin_AB_titre.jpg"
        obtained_out = phys[0]['label']
        self.assertEqual(desired_out, obtained_out,  "Physical Structure "\
                "missmatch: %s != %s" % (desired_out, obtained_out))

class MetsParserOK (unittest.TestCase):
    """
    Test DocumentParser Class.
    """

    def testMetsParser(self):
        """Check MetsParser instance."""
        mets_file = file(mets_file_name)
        mets_parser = MetsParser(mets_file, 'http://doc.rero.ch')
        self.assert_ (mets_parser, "Can not create simple MetsParser Object")
    
    def testMetsBadParser(self):
        """Check Mets instance with a bad file."""
        mets_file = file(pdf_file_name)
        self.assertRaises(multivio.parser.ParserError.InvalidDocument,
                MetsParser, mets_file, 'http://doc.rero.ch')

    def testMetsParserMeta(self):
        """Get Mets Metadata."""
        mets_file = file(mets_file_name)
        mets_parser = MetsParser(mets_file, 'http://doc.rero.ch')
        meta = mets_parser.get_metadata()
        title = meta['title']
        ref_title = 'D. Joh. Sal. Semlers Antwort auf das Bahrdische Glaubensbekenntnis'
        self.assertEqual(title, ref_title, "Metadata has not been "\
            "correctly detected '%s' != '%s'" % (title, 
            u"D. Joh. Sal. Semlers Antwort auf das Bahrdische "\
            "Glaubensbekenntnis"))
    
    def testMetsParserLogical(self):
        """Get Mets logical structure."""
        mets_file = file(mets_file_name)
        mets_parser = MetsParser(mets_file, 'http://doc.rero.ch')
        logic = mets_parser.get_logical_structure()
        sect1_obtained = logic[0]['label']
        sect1_desired = 'Titelblatt'
        self.assertEqual (sect1_desired, sect1_obtained, "TOC is not valid %s != %s" % (sect1_desired, sect1_obtained) )

    def testMetsParserSimpleAuthor(self):
        """Get Mets authors simple."""
        mets_file = file("examples/document_author_simple.mets")
        mets_parser = MetsParser(mets_file, 'http://doc.rero.ch')
        metadata = mets_parser.get_metadata()
        sect1_obtained = metadata['creator'][0]
        sect1_desired = 'Hunt, Robert'
        self.assertEqual (sect1_desired, sect1_obtained, "Author is not valid %s != %s" % (sect1_desired, sect1_obtained) )

    def testMetsParserPhysical(self):
        """Get Mets physical structure."""
        mets_file = file(mets_file_name)
        mets_parser = MetsParser(mets_file, 'http://doc.rero.ch')
        phys = mets_parser.get_physical_structure()
        desired_out =  u"00000001.jpg"
        obtained_out = phys[0]['label']
        self.assertEqual(desired_out, obtained_out,  "Physical Structure "\
                "missmatch: '%s' != '%s'" % (desired_out, obtained_out))

class MarcParserOK (unittest.TestCase):
    """
    Test ParchParser Class.
    """

    def testMarcParser(self):
        """Check MarcParser instance."""
        marc_file = file(marc_file_name)
        marc_parser = MarcParser(marc_file, 'http://doc.rero.ch')
        self.assert_ (marc_parser, "Can not create simple MarcParser Object")
    
    def testMarcBadParser(self):
        """Check Marc instance with a bad file."""
        marc_file = file(pdf_file_name)
        self.assertRaises(multivio.parser.ParserError.InvalidDocument,
                MarcParser, marc_file, 'http://doc.rero.ch')

    def testMarcParserMeta(self):
        """Get Marc Metadata."""
        marc_file = file(marc_file_name)
        marc_parser = MarcParser(marc_file, 'http://doc.rero.ch')
        meta = marc_parser.get_metadata()
        title = meta['title']
        ref_title = 'Phylogeography of Populus alba (L.) and Populus tremula '\
            '(L.) in Central Europe: secondary contact and hybridisation during '\
            'recolonisation from disconnected refugia'
        self.assertEqual(title, ref_title, "Metadata has not been "\
            "correctly detected '%s' != '%s'" % (title, ref_title))
    
    def testMarcParserLogical(self):
        """Get Marc logical structure."""
        marc_file = file(marc_file_name)
        marc_parser = MarcParser(marc_file, 'http://doc.rero.ch')
        logic = marc_parser.get_logical_structure()
        self.assertEqual (logic, None)

    def testMetsParserPhysical(self):
        """Get Marc physical structure."""
        marc_file = file(marc_file_name)
        marc_parser = MarcParser(marc_file, 'http://doc.rero.ch')
        phys = marc_parser.get_physical_structure()
        desired_out =  u"pdf"
        obtained_out = phys[0]['label']
        self.assertEqual(desired_out, obtained_out,  "Physical Structure "\
                "missmatch: '%s' != '%s'" % (desired_out, obtained_out))

class ModsParserOK (unittest.TestCase):
    """
    Test ModsParser Class.
    """

    def testModsParser(self):
        """Check ModsParser instance."""
        mods_file = file(mods_file_name)
        mods_parser = ModsParser(mods_file, 'http://doc.rero.ch')
        self.assert_ (mods_parser, "Can not create simple ModsParser Object")
    
    def testModsBadParser(self):
        """Check Mods instance with a bad file."""
        mods_file = file(pdf_file_name)
        self.assertRaises(multivio.parser.ParserError.InvalidDocument,
                ModsParser, mods_file, 'http://doc.rero.ch')

    def testModsParserMeta(self):
        """Get Mods Metadata."""
        mods_file = file(mods_file_name)
        mods_parser = ModsParser(mods_file, 'http://doc.rero.ch')
        meta = mods_parser.get_metadata()
        title = meta['title']
        ref_title = 'Phylogeography of Populus alba (L.) and Populus tremula '\
            '(L.) in Central Europe: secondary contact and hybridisation during '\
            'recolonisation from disconnected refugia'
        self.assertEqual(title, ref_title, "Metadata has not been "\
            "correctly detected '%s' != '%s'" % (title, ref_title))
    
    def testModsParserLogical(self):
        """Get Mods logical structure."""
        mods_file = file(mods_file_name)
        mods_parser = ModsParser(mods_file, 'http://doc.rero.ch')
        logic = mods_parser.get_logical_structure()
        self.assertEqual (logic, None)

    def testModsParserPhysical(self):
        """Get Mods physical structure."""
        mods_file = file(mods_file_name)
        mods_parser = ModsParser(mods_file, 'http://doc.rero.ch')
        phys = mods_parser.get_physical_structure()
        desired_out =  u"pdf"
        obtained_out = phys[0]['label']
        self.assertEqual(desired_out, obtained_out,  "Physical Structure "\
                "missmatch: '%s' != '%s'" % (desired_out, obtained_out))

if __name__ == '__main__':
    # the main program if we execute directly this module

    # do all the tests
    unittest.main()
