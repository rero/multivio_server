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
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

# local modules
from parser import DocumentParser

#----------------------------------- Classes -----------------------------------

class ImgParser(DocumentParser):
    """To parse PDF document"""

    def __init__(self, file_stream, url, mime):
        DocumentParser.__init__(self, file_stream)
        self._url = url
        self._mime = mime
        import Image
        img = Image.open(file_stream)
        (self._width, self._height) = img.size

    def _check(self):
        """Check if the pdf is valid."""
        return True

    def getMetaData(self):
        """Get pdf infos."""

        metadata = {}
        metadata['title'] = self._url.split('/')[-1]
        metadata['mime'] = self._mime
        metadata['width'] = self._width
        metadata['height'] = self._height

        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    



#---------------------------- Main Part ---------------------------------------
def main():
    """Main function"""
    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("To test the Logger class.")

    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)

    parser.add_option ("-p", "--port", dest="port",
                       help="Http Port (Default: 4041)",
                       type="int", default=4041)

    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")

    from wsgiref.simple_server import make_server
    application = LoggerApp()
    server = make_server('', options.port, application)
    server.serve_forever()

if __name__ == '__main__':
    main()

