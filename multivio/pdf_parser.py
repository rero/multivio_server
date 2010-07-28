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
import re
from optparse import OptionParser
import pyPdf
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

# local modules
from parser import DocumentParser, ParserError

#----------------------------------- Classes -----------------------------------

class PdfParser(DocumentParser, pyPdf.PdfFileReader):
    """To parse PDF document"""

    def __init__(self, file_stream, url, label):
        DocumentParser.__init__(self, file_stream)
        self._url = url
        self._label = label
        self._page_id_to_page_numbers = None

    def __initpdf__(self, stream):
        """Initialize the PdfFileReader with a new file stream"""
        #call pdf reader parent
        pyPdf.PdfFileReader.__init__(self, stream)

        def _setup_page_id_to_num(pages=None, _result=None, _num_pages=None):
            """to link page number with TOC entries. Stolen from:
            http://stackoverflow.com/questions/1918420/split-a-pdf-based-on-outline
            """
            if _result is None:
                _result = {}
            if pages is None:
                _num_pages = []
                pages = self.trailer["/Root"].getObject()["/Pages"].getObject()
            t = pages["/Type"]
            if t == "/Pages":
                for page in pages["/Kids"]:
                    # +1 patch from original code (first page is 1 and not 0)
                    _result[page.idnum] = len(_num_pages) + 1
                    _setup_page_id_to_num(page.getObject(), _result, _num_pages)
            else:
                if t == "/Page":
                    _num_pages.append(1)
            return _result
        self._page_id_to_page_numbers = _setup_page_id_to_num()

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
        try:
            self.__initpdf__(self._file_stream)
        except:
            self.logger.debug("Cannot extract page from pdf.")
            raise ParserError.InvalidDocument("Cannot extract page from pdf.")

        metadata = {}
        info = None
        try:
            info = self.getDocumentInfo()
        except Exception:
            self.logger.debug("Do not find info in pdf.")
        if info and info.title is not None and len(info.title) > 0 \
                and self.has_toc(self.getOutlines()):
            metadata['title'] = info.title
        else:
            metadata['title'] = 'PDF Document'
            pdf_file_parts = self._url.split('/')
            if len(pdf_file_parts) > 0:
                if re.match('.*?\.pdf', pdf_file_parts[-1]):
                    metadata['title'] = pdf_file_parts[-1]

        if info and info.author is not None and len(info.author) > 0:
            metadata['creator'] = [info.author]
        else:
            metadata['creator'] = ['']
        metadata['nPages'] = self.getNumPages()
        metadata['mime'] = 'application/pdf'
        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    
    def has_toc(self, outlines):
        """Return True if the pdf contains a Table of Contents."""
        if outlines is None:
            return False
        for obj in outlines:
            if isinstance(obj, pyPdf.pdf.Destination):
                return True
        return False

    def get_logical_structure(self):
        """Get the logical structure of the pdf, basically the TOC."""
        try:
            self.__initpdf__(self._file_stream)
        except Exception:
            raise ParserError.InvalidDocument("Cannot extract page from pdf.")
        to_return = None

        #recursive fnct
        def get_parts(data, space=' '):
            """Recursive function to go through the TOC of the pdf."""
            to_return = []
            for obj in data:
                if isinstance(obj, pyPdf.pdf.Destination) and not \
                    isinstance(obj.page, pyPdf.generic.NullObject):
                    title = obj.title
                    if not isinstance(title, unicode):
                        import chardet
                        encoding = chardet.detect(title)['encoding']
                        if not re.match('ascii', encoding):
                            title = title.decode(encoding)
                            title = title.encode('utf-8')
                    pagenr = self._page_id_to_page_numbers.get(obj.page.idnum, 
                                '???')
                    #print "%s%s %s" % (space, title, pagenr)
                    to_return.append({
                                        'label' : title,
                                        'file_position' : {
                                            'index' : pagenr,
                                            'url'   : self._url
                                        }
                                    })
                elif isinstance(obj, list):
                    parts =  get_parts(obj, space + "  ")
                    if len(parts) > 0:
                        if len(to_return) > 0:
                            to_return[-1]['childs'] = parts
                        else:
                            to_return = parts
            return to_return
        try:
            outlines = self.getOutlines()
            self.logger.debug("TOC found.")
        except:
            outlines = None
            self.logger.debug("No TOC found.")
        if outlines is not None:
            to_return = get_parts(self.getOutlines())
            self.logger.debug("Table Of Content: %s"% json.dumps(to_return, 
                    sort_keys=True, indent=4))
        # to solve empty TOC for
        # ex:http://www.fr.ch/bcu/n/genealogies/Banquetaz_description.pdf

        if len(to_return) == 0:
            return None
        return to_return

    def get_physical_structure(self):
        """Get the physical structure of the pdf."""
        phys_struct = [{
                          'url': self._url,
                          'label': self._label
                      }]
        self.logger.debug("Physical Structure: %s"% json.dumps(phys_struct,
                sort_keys=True, indent=4))
        return phys_struct
    
    def display_toc(self):
        """ Print on stdout the Table of content with the page number.
        """
        self.logger.debug("Get TOC")
        try:
            self.__initpdf__(self._file_stream)
        except Exception:
            self.logger.debug("Cannot extract page from pdf.")
            raise ParserError.InvalidDocument("Cannot extract page from pdf.")
        
        #recursive fnct
        def print_part(data, space=' '):
            for obj in data:
                if isinstance(obj, pyPdf.pdf.Destination) and not \
                    isinstance(obj.page, pyPdf.generic.NullObject):
                    title = obj.title
                    if not isinstance(title, unicode):
                        import chardet
                        encoding = chardet.detect(title)['encoding']
                        if not re.match('ascii', encoding):
                            title = title.decode(encoding)
                            title = title.encode('utf-8')
                    pagenr = self._page_id_to_page_numbers.get(obj.page.idnum,
                        '???')
                elif isinstance(obj, list):
                    print_part(obj, space + "  ")
        try:
            outlines = self.getOutlines()
        except:
            outlines = None
        outlines = self.getOutlines()
        if outlines is not None:
            print_part(self.getOutlines())


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

    pdf_file = file(args[0])    
    parser = PdfParser(pdf_file, '', '')
    parser.display_toc()
    toc = parser.get_logical_structure()
    print toc
if __name__ == '__main__':
    main()

