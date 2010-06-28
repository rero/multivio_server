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
import Image

#----------------------------------- Exceptions --------------------------------

#----------------------------------- Classes -----------------------------------

#_______________________________________________________________________________
class ImageProcessor(DocumentProcessor):
    """Class to process pdf document"""
#_______________________________________________________________________________
    def __init__(self, file_name):
        DocumentProcessor.__init__(self, file_name)
        self._img = Image.open(file_name)

    def _check(self):
        """Check if the document is valid."""
        return True

    def render(self, max_output_size=None, angle=0, index=None,
        output_format=None):
        """Render the document content.

            max_output_size -- tupple: maximum dimension of the output
            angle -- int: angle in degree
            index -- dict: index in the document
            output_format -- string: select the output format
            
        return:
            mime_type -- string: output mime type
            data -- string: output data
        """
        output_format = output_format or 'image/jpeg'
        self.logger.debug("Render Image")
        max_width = max_output_size[0] or self._img.size[0]
        max_height = max_output_size[1] or self._img.size[1]

        self._img.thumbnail((max_width, max_height), Image.ANTIALIAS)
        self.logger.debug("Rotate the image: %s degree" % angle)
        if angle != 0:
            self._img = self._img.rotate(angle)
        f = cStringIO.StringIO()
        #img.save(f, "PNG")
        self.logger.debug("Out format: %s", output_format)
        if re.match(r'.*?/jpeg', output_format):
            self._img.save(f, "JPEG", quality=90)
            mime_type = 'image/jpeg'
        else:
            self._img.save(f, "PNG")
            mime_type = 'image/png'
        f.seek(0)
        content = f.read()
        return(mime_type, content)
