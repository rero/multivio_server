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
from optparse import OptionParser
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
import re

# local modules
from mvo_config import MVOConfig
from web_app import WebApplication

from pdf_parser import PdfParser
from dc_parser import DublinCoreParser
from image_parser import ImgParser
from mets_parser import MetsParser
from marc_parser import MarcParser
import parser
from web_app import ApplicationError


#------------------ Classes ----------------------------
class DocParserApp(WebApplication):
    """ Parser chooser or selector.
        
        Based on the mime type it select the right chooser and return a vaild
        http response.
    """
    def __init__(self, temp_dir=MVOConfig.General.temp_dir):
        """ Build and instance used by the dispatcher.

         Keyword arguments:
            counter -- int: initial value for the node counter
            sequence_number -- int: initial value for the sequence number often
                                    usefull for parser of parsers
        """
        WebApplication.__init__(self, temp_dir)


        self.usage = """ Using the GET method it return the metadata, the
        logical structure and the physical structure in json format.<br>
<h2>Arguments:</h2>
<ul> 
    <li><em>url --string--</em>  url of a xml/pdf file representing the record.  
</ul> 
<h2>Examples:</h2>

<h3>GetMetadata:</h3>
<ul> 
<li><a href="/server/metadata/get?url=http://doc.rero.ch/record/9264/export/xd?"><b>Simple Dublin Core.</b></a>
<li><a
href="/server/metadata/get?url=http://doc.rero.ch/lm.php?url=1000,40,6,20091106095458-OI/2009INFO006.pdf"><b>Simple Pdf.</b></a>
<li><a
href="/server/metadata/get?url=http://doc.rero.ch/record/12703/export/xd?"><b>Dublin
Core with Pdfs inside..</b></a>
</ul>

<h4>Examples Mets:</h4>
<ul> 
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN338271201"><b>DFG Example 110 pages, 4 labels+titre.</b></a>
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574578609"><b>DFG Example: 165 pages, 26 labels + titre.</b></a>
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN243574339"><b>DFG Example: 421 pages, 71 labels + titre.</b></a>
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN326329617"><b>DFG Example: 15 pages, 3 labels + titre, fichier rattaché au root.</b></a>
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN58460422X"><b>DFG Example: 172 pages, 4 labels + titre.</b></a>
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574841571"><b>DFG Example: 276 pages, 24 labels + titre.</b></a>
</ul>
<h4>Examples Pdf:</h4>
<ul> 
<li><a href="/server/metadata/get?url=http://doc.rero.ch/lm.php?url=1000,40,4,20091104141001-BU/Th_FautschC.pdf"><b>PDF with TOC.</b></a>
</ul>

<h3>GetLogicalStructure:</h3>
<ul> 
<li><a href="/server/structure/get_logical?url=http://doc.rero.ch/record/9264/export/xd?"><b>Simple Dublin Core.</b></a>
<li><a
href="/server/structure/get_logical?url=http://doc.rero.ch/lm.php?url=1000,40,6,20091106095458-OI/2009INFO006.pdf"><b>Simple Pdf.</b></a>
<li><a
href="/server/structure/get_logical?url=http://doc.rero.ch/record/12703/export/xd?"><b>Dublin
Core with Pdfs inside..</b></a>
</ul>

<h4>Examples Mets:</h4>
<ul> 
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN338271201"><b>DFG Example 110 pages, 4 labels+titre.</b></a>
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574578609"><b>DFG Example: 165 pages, 26 labels + titre.</b></a>
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN243574339"><b>DFG Example: 421 pages, 71 labels + titre.</b></a>
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN326329617"><b>DFG Example: 15 pages, 3 labels + titre, fichier rattaché au root.</b></a>
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN58460422X"><b>DFG Example: 172 pages, 4 labels + titre.</b></a>
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574841571"><b>DFG Example: 276 pages, 24 labels + titre.</b></a>
</ul>
<h4>Examples Pdf:</h4>
<ul> 
<li><a href="/server/structure/get_logical?url=http://doc.rero.ch/lm.php?url=1000,40,4,20091104141001-BU/Th_FautschC.pdf"><b>PDF with TOC.</b></a>
</ul>

<h3>GetPhysicalStructure:</h3>
<ul> 
<li><a href="/server/structure/get_physical?url=http://doc.rero.ch/record/9264/export/xd?"><b>Simple Dublin Core.</b></a>
<li><a
href="/server/structure/get_physical?url=http://doc.rero.ch/lm.php?url=1000,40,6,20091106095458-OI/2009INFO006.pdf"><b>Simple Pdf.</b></a>
<li><a
href="/server/structure/get_physical?url=http://doc.rero.ch/record/12703/export/xd?"><b>Dublin
Core with Pdfs inside..</b></a>
</ul>

<h4>Examples Mets:</h4>
<ul> 
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN338271201"><b>DFG Example 110 pages, 4 labels+titre.</b></a>
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574578609"><b>DFG Example: 165 pages, 26 labels + titre.</b></a>
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN243574339"><b>DFG Example: 421 pages, 71 labels + titre.</b></a>
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN326329617"><b>DFG Example: 15 pages, 3 labels + titre, fichier rattaché au root.</b></a>
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN58460422X"><b>DFG Example: 172 pages, 4 labels + titre.</b></a>
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574841571"><b>DFG Example: 276 pages, 24 labels + titre.</b></a>
</ul>
<h4>Examples Pdf:</h4>
<ul> 
<li><a href="/server/structure/get_physical?url=http://doc.rero.ch/lm.php?url=1000,40,4,20091104141001-BU/Th_FautschC.pdf"><b>PDF with TOC.</b></a>
</ul>
"""
    
    def get(self, environ, start_response):
        """ Callback method for new http request.
        
        """
        #get parameters from the URI
        (path, opts) = self.get_params(environ)

        #check if is valid
        self.logger.info("Accessing: %s with opts: %s" % (path, opts))

        if re.search(r'metadata/get', path) is not None:
            self.logger.debug("Get Metadata with opts: %s" % opts)
            if opts.has_key('url'):
                metadata = self.get_metadata(opts['url'])
                start_response('200 OK', [('content-type',
                    'application/json')])
                return ["%s" % metadata]

        if re.search(r'structure/get_logical', path) is not None:
            self.logger.debug("Get Logical with opts: %s" % opts)
            if opts.has_key('url'):
                logical = self.get_logical_structure(opts['url'])
                start_response('200 OK', [('content-type',
                    'application/json')])
                return ["%s" % logical]

        if re.search(r'structure/get_physical', path) is not None:
            self.logger.debug("Get Physical with opts: %s" % opts)
            if opts.has_key('url'):
                physical = self.get_physical_structure(opts['url'])
                start_response('200 OK', [('content-type',
                    'application/json')])
                return ["%s" % physical]
        raise ApplicationError.InvalidArgument("Invalid Argument")

    def _choose_parser(self, content, url, mime):
        """Select the right parser given the mime type."""
        if re.match('.*?/pdf.*?', mime):
            self.logger.info("Pdf parser found!")
            return PdfParser(content, url, url.split('/')[-1])
        
        if re.match('image/.*?', mime):
            self.logger.info("Image parser found!")
            return ImgParser(content, url, mime)

        if re.match('.*?/xml.*?', mime):
            #some METS files contain uppercase mets directive
            self.logger.info("XML parser found!")
            content_str = content.read()
            content.seek(0)
            content_str = content_str.replace('METS=', 'mets=')
            content_str = content_str.replace('METS:', 'mets:')
            content_str = content_str.replace('MODS=', 'mods=')
            content_str = content_str.replace('MODS:', 'mods:')
            
            #METS parser
            selected_parser = None
            try:
                self.logger.debug("Try Mets parser!")
                selected_parser = MetsParser(content, url)
                self.logger.info("Mets parser found!")
            except parser.ParserError.InvalidDocument:
                self.logger.debug('Cannot be parsed by Mets parser')
            try:
                self.logger.debug("Try DC parser!")
                selected_parser = DublinCoreParser(content, url)
                self.logger.info("DubinCore parser found!")
            except parser.ParserError.InvalidDocument:
                self.logger.debug('Cannot be parsed by DC parser')

            try:
                self.logger.debug("Try Marc parser!")
                selected_parser = MarcParser(content, url)
                self.logger.info("Marc parser found!")
            except parser.ParserError.InvalidDocument:
                self.logger.debug('Cannot be parsed by Marc parser')
            if selected_parser:
                return selected_parser
            else:
                self.logger.warn("XML format not supported for %s" % url)
                raise ApplicationError.UnsupportedFormat(
                    "XML format not supported for %s" % url)

    def get_metadata(self, url):
        """Get the internal metadata of a document."""
        (local_file, mime) = self.get_remote_file(url)
            
        content = file(local_file,'r')

        #check the mime type
        self.logger.debug("Url: %s Detected Mime: %s" % (url, mime))
        selected_parser = self._choose_parser(content, url, mime)
        metadata = selected_parser.get_metadata()
        metadata['mime'] = mime
            
        return json.dumps(metadata,  sort_keys=True, indent=2)

    def get_logical_structure(self, url):
        """Get the internal structure of a document such as Table of
        content."""
        (local_file, mime) = self.get_remote_file(url)
        content = file(local_file,'r')

        #check the mime type
        selected_parser = self._choose_parser(content, url, mime)
        logic = selected_parser.get_logical_structure()
        #logic['mime'] = mime
            
        return json.dumps(logic,  sort_keys=True, indent=2)

    def get_physical_structure(self, url):
        """Get the list of physical files such as pdf or images."""
        (local_file, mime) = self.get_remote_file(url)
        content = file(local_file,'r')

        #check the mime type
        selected_parser = self._choose_parser(content, url, mime)
        physic = selected_parser.get_physical_structure()
        #physic['mime'] = mime
            
        return json.dumps(physic,  sort_keys=True, indent=2)

    def get_params(self, environ):
        """ Overload the default method to allow cgi url.
            
            The url parameter should be at the end of the url.
            i.e.
            /server/structure/get_logical?format=raw&url=http:www.toto.ch/test?url=http://www.test.ch
            is ok, but:
            /server/structure/get_logical?url=http:www.toto.ch/test?url=http://www.test.ch&format=raw
            is incorrect.
        """
        path = environ['PATH_INFO']
        opts = {}
        to_parse = environ['QUERY_STRING']
        if len(to_parse) > 0:
            res = list(re.match(r'[(.*?)&]{0,1}url=(.*)', to_parse).groups())
            #replace all until the first occurence of url=
            opts['url'] = res.pop()
            if len(res) > 0:
                for val in res:
                    args = val.split('&')
                    for arg in args:
                        res_args = list(re.match(r'(.*?)=(.*)', arg).groups())
                        opts[res_args[0]] = res_args[1]
                    
        return (path, opts)

            
    
#---------------------------- Main Part ---------------------------------------
def main():
    """Main function"""
    usage = "usage: %prog [options]"

    opt_parser = OptionParser(usage)

    opt_parser.set_description ("To test the Logger class.")

    opt_parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)

    opt_parser.add_option ("-p", "--port", dest="port",
                       help="Http Port (Default: 4041)",
                       type="int", default=4041)

    (options, args) = opt_parser.parse_args()

    if len(args) != 0:
        opt_parser.error("Error: incorrect number of arguments, try --help")

    from wsgiref.simple_server import make_server
    application = DocParserApp()
    server = make_server('', options.port, application)
    server.serve_forever()

if __name__ == '__main__':
    main()

