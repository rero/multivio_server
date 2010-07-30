#!/usr/bin/env python
"""Document Parser module for Multivio"""
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules ---------------------------------------

# import of standard modules
import sys
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
from xml.dom.minidom import parseString

# local modules
from parser import DocumentParser, ParserError

#----------------------------------- Classes -----------------------------------

class ModsParser(DocumentParser):
    """To parse XMLMods document"""

    def __init__(self, file_stream, url):
        DocumentParser.__init__(self, file_stream)
        self._url = url

    def _check(self):
        """Check if the pdf is valid."""
        self._file_stream.seek(0)
        content_str = self._file_stream.read()
        try:
            doc = parseString(content_str)
        except Exception:
            return False
        mods = doc.getElementsByTagName('modsCollection')
        if len(mods) and mods[0].namespaceURI == \
            'http://www.loc.gov/mods/v3':
            return True
        return False

    def _get_record(self):
        """Get the record object in the xml file."""
        self._file_stream.seek(0)
        content_str = self._file_stream.read()
        doc = parseString(content_str)
        
        records = doc.getElementsByTagName('mods')

        # get the id number of the first record
        if len(records) == 0:
            raise ParserError.InvalidDocument(
                "XML/Mods Core document should contains at lease one record!")
        if len(records) > 1:
            raise ParserError.InvalidDocument(
                "XML/Mods Core document should not contains more than "\
                "one record!")
        return records[0]

    def get_metadata(self):
        """Get pdf infos."""
        record = self._get_record()
        metadata = {}
        title_info = record.getElementsByTagName('titleInfo')
        if len(title_info) > 0:
            title = title_info[0].getElementsByTagName('title')
            if len(title) > 0:
                metadata['title'] = \
                    title[0].firstChild.nodeValue.encode('utf-8')

        names = record.getElementsByTagName('name')
        creator = []
        if len(names) > 0:
            for name in names:
                first_and_last_name = name.getElementsByTagName('namePart')
                if len(first_and_last_name) > 0:
                    creator.append(
                        first_and_last_name[0].firstChild.nodeValue.encode('utf-8'))
        if len(creator) > 0:
            metadata['creator'] = " ".join(creator)
        language_info = record.getElementsByTagName('language')
        if len(language_info) > 0:
            language = language_info[0].getElementsByTagName('languageTerm')
            if len(language) > 0:
                metadata['language'] = \
                    language[0].firstChild.nodeValue.encode('utf-8')
        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    
    def get_physical_structure(self):
        """Get the physical structure of the pdf."""
        phys_struct = []
        record = self._get_record()
        urls = []
        labels = []
        locations = record.getElementsByTagName('location')

        for location in locations:
            urls_info = location.getElementsByTagName('url')
            for url_info in urls_info:
                if url_info.getAttribute('access').encode('utf-8') \
                    == 'raw object':
                    urls.append(url_info.firstChild.nodeValue.encode('utf-8'))
                    labels.append(
                        url_info.getAttribute('displayLabel').encode('utf-8'))
        for i in range(len(urls)):
            phys_struct.append({
                'url': urls[i].decode('utf-8'),
                'label': labels[i].decode('utf-8')
            })
        self.logger.debug("Physical Structure: %s"% json.dumps(phys_struct,
                sort_keys=True, indent=4))
        return phys_struct


