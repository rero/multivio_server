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
import sys
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

# local modules
from parser import DocumentParser

#----------------------------------- Classes -----------------------------------

class ImgParser(DocumentParser):
    """To parse PDF document"""

    def __init__(self, file_stream, url, label, mime):
        DocumentParser.__init__(self, file_stream)
        self._url = url
        self._label = label
        self._mime = mime
        import Image
        img = Image.open(file_stream)
        (self._width, self._height) = img.size

    def _check(self):
        """Check if the pdf is valid."""
        return True

    def get_metadata(self):
        """Get pdf infos."""

        metadata = {}
        metadata['title'] = self._url.split('/')[-1]
        metadata['mime'] = self._mime
        metadata['fileSize'] = self.get_file_size()
        #metadata['width'] = self._width
        #metadata['height'] = self._height

        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    
    def get_physical_structure(self):
        """Get the physical structure of the pdf."""
        phys_struct = [{
                          'url': self._url,
                          'label': self._label
                      }]
        self.logger.debug("Physical Structure: %s"% json.dumps(phys_struct,
                sort_keys=True, indent=4))
        return phys_struct
