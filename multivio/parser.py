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
import logging

# local modules
import logger
from mvo_config import MVOConfig

#----------------------------------- Exceptions --------------------------------

class ParserError:
    """Base class for errors in the DocumentParser packages."""
    class InvalidDocument(Exception):
        """The document is not valid."""
        pass
    class InvalidParameters(Exception):
        """The type of the input parameters is not correct."""
        pass

#----------------------------------- Classes -----------------------------------

#_______________________________________________________________________________
class DocumentParser(object):
    """Base class to parse document"""

    def __init__(self, file_stream):
        """Constructor."""
        self._file_stream = file_stream
        self.logger = logging.getLogger(MVOConfig.Logger.name + "."
                        + self.__class__.__name__) 
        if self._check() is not True:
            raise ParserError.InvalidDocument("The file is invalid. (is it" \
                    "corrupted?)")

    def _check(self):
        """Check if the document is valid."""
        return True

    def get_metadata(self):
        """Get the Metadata of the document.
        Such as title, author, etc.
        """
        return None

    def get_logical_structure(self):
        """Get the logical structure of the document.
        Such as Table of Contents.
        """
        return None
    
    def get_file_size(self):
        """
            Get the file size of the current file.
        """
        self._file_stream.seek(0, 2)
        file_size = self._file_stream.tell()
        self._file_stream.seek(0)
        return file_size

    def get_physical_structure(self):
        """Get the physical structure of the document.
        Such as list of images.
        """
        return None


