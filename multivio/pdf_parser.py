#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Document Parser module for Multivio"""

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules ---------------------------------------

# import of standard modules
import re
import poppler
from optparse import OptionParser

# local modules
from parser import DocumentParser, ParserError

#----------------------------------- Classes -----------------------------------

class PdfParser(DocumentParser):
    """To parse PDF document"""

    def __init__(self, file_name,  url, label):
        file_stream = file(file_name)
        DocumentParser.__init__(self, file_stream)
        self._url = url
        self._label = label
        self._page_id_to_page_numbers = None
        self._doc = poppler.PDFDoc(file_name)


    def _check(self):
        """Check if the pdf is valid."""
        current_pos = self._file_stream.tell()
        self._file_stream.seek(0)
        first_line = self._file_stream.readline()
        self._file_stream.seek(current_pos)
        if first_line.startswith('%PDF'):
            return True
        return False

    def get_metadata(self):
        """Get pdf infos."""
        self.logger.debug("Get Metadata")
        metadata = {}
        infos = self._doc.getInfo()
        metadata['title'] = ""
        metadata['creator'] = [""]
        try:
            metadata['title'] = infos['Title']
        except KeyError:
            metadata['title'] = 'PDF Document'
            pdf_file_parts = self._url.split('/')
            if len(pdf_file_parts) > 0:
                if re.match('.*?\.pdf', pdf_file_parts[-1]):
                    metadata['title'] = pdf_file_parts[-1]
        try:
            metadata['creator'] = infos['Author']
        except KeyError:
            pass
        metadata['mime'] = 'application/pdf'
        metadata['nPages'] = self._doc.getNumPages()
        #info = None
        #try:
        #    info = self.getDocumentInfo()
        #except Exception:
        #    self.logger.info("Do not find info in pdf.")
        #if info and info.title is not None and len(info.title) > 0 \
        #        and self.has_toc(self.getOutlines()):
        #    metadata['title'] = info.title
        #else:
        #    metadata['title'] = 'PDF Document'
        #    pdf_file_parts = self._url.split('/')
        #    if len(pdf_file_parts) > 0:
        #        if re.match('.*?\.pdf', pdf_file_parts[-1]):
        #            metadata['title'] = pdf_file_parts[-1]

        #if info and info.author is not None and len(info.author) > 0:
        #    metadata['creator'] = [info.author]
        #else:
        #    metadata['creator'] = ['']
        #metadata['nPages'] = self.getNumPages()
        #metadata['mime'] = 'application/pdf'
        #self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
        #                indent=4))
        return metadata
    

    def get_logical_structure(self):
        """Get the logical structure of the pdf, basically the TOC."""
        toc = self._doc.getToc()
        if len(toc) < 1:
            return None
        def add_file_index(entries):
            """Recursive function."""
            for entry in entries:
                page_nr = entry['page_number']
                entry['file_position'] = {
                    'index' : page_nr,
                    'url' : self._url     
                    }
                del entry['page_number']
                if entry.has_key('childs'):
                    add_file_index(entry['childs'])
        add_file_index(toc)
        return toc

    def get_physical_structure(self):
        """Get the physical structure of the pdf."""
        phys_struct = [{
                          'url': self._url,
                          'label': self._label
                      }]
        return phys_struct
    


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

    if len(args) != 1:
        parser.error("Error: incorrect number of arguments, try --help")

    parser = PdfParser(args[0], '', '')
    #info = parser.get_logical_structure()
    #print info
    toc = parser.get_logical_structure()
    import pprint
    pprint.pprint(toc)
    info = parser.get_metadata()
    pprint.pprint(info)

if __name__ == '__main__':
    main()

