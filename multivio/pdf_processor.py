#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Document Parser module for Multivio"""

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules ---------------------------------------

# import of standard modules
import sys
import os
from optparse import OptionParser
import pyPdf
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
import re
import cStringIO

# local modules
import logger
import logging
from processor import DocumentProcessor
from mvo_config import MVOConfig
import poppler
from web_app import ApplicationError

#----------------------------------- Exceptions --------------------------------

#----------------------------------- Classes -----------------------------------

#_______________________________________________________________________________
class PdfProcessor(DocumentProcessor):
    """Class to process pdf document"""
#_______________________________________________________________________________
    def __init__(self, file_name):
        DocumentProcessor.__init__(self, file_name)
        poppler.cvar.globalParams.setEnableFreeType("yes")
        poppler.cvar.globalParams.setAntialias("yes")
        poppler.cvar.globalParams.setVectorAntialias("yes")
        self._doc = poppler.PDFDoc(self._file_name)

    def _check(self):
        """Check if the document is valid."""
        return True

    def render(self, max_output_size=None, angle=0, index=None, output_format=None):
        """Render the document content.

            max_output_size -- tupple: maximum dimension of the output
            angle -- int: angle in degree
            index -- dict: index in the document
            output_format -- string: select the output format
            
        return:
            mime_type -- string: output mime type
            data -- string: output data
        """
        self.logger.debug("Render")
        return self._getImageFromPdf(page_nr=index['page_number'],
            max_width=max_output_size[0], max_height=max_output_size[1],
            angle=angle, output_format=output_format)

    def search(self, query, from_=None, to_=None, max_results=None, sort=None):
        """Search parts of the document that match the given query.

            from_ -- dict: start the search at from_
            to_ -- dict: end the search at to_
            max_results -- int: limit the number of the returned results
            sort -- string: sort the results given the sort criterion
        return:
            a dictionary with the founded results
        """
        return None

    def indexing(self, output_file):
        """Batch indexing of the document.
        return:
            True if everything is ok.
        """
        return None

    def _getOptimalScale(self, max_width, max_height, page_nr):
        if max_width is None and max_height is None:
            return 1.0
        page_width = self._doc.getPageMediaWidth(page_nr)
        page_height = self._doc.getPageMediaHeight(page_nr)
        page_ratio = page_height/float(page_width)
        if max_width is None:
            max_width = max_height/page_ratio
        if max_height is None:
            max_height = max_width*page_ratio
        scale = max_width/page_width
        if max_height < (page_height*scale):
            scale = max_height/page_height
        return scale

    def _getImageFromPdf(self, page_nr=1, max_width=None, max_height=None, angle=0, output_format='JPEG'):
        if self._doc.getNumPages() < page_nr:
            raise ApplicationError.InvalidArgument("Bad page number: it should be < %s."
                % self._doc.getNumPages())
        import time
        self.logger.debug("Render image from pdf with opts width=%s, height=%s, angle=%s, page_nr=%s." % (max_width, max_height, angle, page_nr))
        start = time.clock()
        splash = poppler.SplashOutputDev(poppler.splashModeRGB8, 3, False,
            (255, 255, 255), True, True)
        splash.startDoc(self._doc.getXRef())

        scale = self._getOptimalScale(max_width, max_height, page_nr)
        self._doc.displayPage(splash, page_nr, 72*scale, 72*scale, 0, True, True, False)

        bitmap = splash.getBitmap()
        new_width = bitmap.getWidth()
        new_height = bitmap.getHeight()
        data = bitmap.getDataPtr()
        import Image
        pil = Image.fromstring('RGB', (new_width, new_height), data)
        if angle != 0:
            pil = pil.rotate(int(angle))
        f = cStringIO.StringIO()
        pil.save(f, "JPEG", quality=90)
        f.seek(0)
        content = f.read()
        self.logger.debug("Total Process Time: %s", (time.clock() - start))
        #header = [('content-type', 'image/jpeg'), ('content-length',
        #str(len(content)))]
        return('image/jpeg', content)

