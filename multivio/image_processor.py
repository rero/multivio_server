#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Document Parser module for Multivio"""

#==============================================================================
#  This file is part of the Multivio software.
#  Project  : Multivio - https://www.multivio.org/
#  Copyright: (c) 2009-2011 RERO (http://www.rero.ch/)
#  License  : See file COPYING
#==============================================================================

__copyright__ = "Copyright (c) 2009-2011 RERO"
__license__ = "GPL V.2"



#---------------------------- Modules ---------------------------------------

# import of standard modules
import re
import cStringIO

# local modules
from processor import DocumentProcessor
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
        output_format=None, restricted=False):
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
        self.logger.info("Render Image: %s" % self._file_name)
        max_width = max_output_size[0] or self._img.size[0]
        max_height = max_output_size[1] or self._img.size[1]

        self._img.thumbnail((max_width, max_height), Image.ANTIALIAS)
        self.logger.debug("Rotate the image: %s degree" % angle)
        if angle != 0:
            self._img = self._img.rotate(angle)
        if restricted:
            (new_width, new_height) = self._img.size()
            if (MVOConfig.Security.img_max_width > max_width)\
                and (MVOConfig.Security.pdf_max_height > new_height):
                raise ApplicationError.PermissionDenied(
                    "Your are not allowed to see this document.")

        temp_file = cStringIO.StringIO()
        #img.save(f, "PNG")
        self.logger.debug("Out format: %s", output_format)
        if re.match(r'.*?/jpeg', output_format):
            self._img.save(temp_file, "JPEG", quality=90)
            mime_type = 'image/jpeg'
        else:
            self._img.save(temp_file, "PNG")
            mime_type = 'image/png'
        temp_file.seek(0)
        content = temp_file.read()
        return(mime_type, content)
    
    def get_size(self, index=None):
        """Return the size of the document content.
            index -- dict: index in the document
            
        return:
            data -- string: output data
        """
        size = {}
        size['width'] = self._img.size[0]
        size['height'] = self._img.size[1]

        return size
