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
from xml.dom.minidom import parseString

# local modules
import logger
import logging
from mvo_config import MVOConfig
from web_app import WebApplication

from pdf_processor import PdfProcessor
from image_processor import ImageProcessor
import processor
from web_app import ApplicationError


#------------------ Classes ----------------------------
class DocProcessorApp(WebApplication):
    """ Parser chooser or selector.
        
        Based on the mime type it select the right chooser and return a vaild
        http response.
    """
    def __init__(self, temp_dir=MVOConfig.General.temp_dir):
        """ Build and instance used by the dispatcher.

         Keyword arguments:
        """
        WebApplication.__init__(self, temp_dir)

        self.usage = """Using the GET method it return a thumbnail in PNG format of a given size for a given
image.<br>
<b>Arguments:</b>
<ul>
<li><em>url --string--</em>  url of an image file.
<li><em>max_width --integer--</em>  max width of the output image in pixel.  Default(None)
<li><em>max_height --integer--</em>  max height of the output image in pixel.  Default(None)
<li><em>page_nr --integer--</em>  extract the page <pagenr>. Pdf only. Default(1).
<li><em>angle --integer--</em>  angle rotation. Default(0).
</ul>
<a
href="/server/document/render?max_width=400&max_height=400&angle=0&url=http://doc.rero.ch/lm.php?url=1000,10,2,20080701134109-FH/Braune_MWK_tab1a.jpg"><b>Image
example.</b></a><br>
<a
href="/server/document/render?max_width=800&max_height=400&angle=0&page_nr=2&url=http://doc.rero.ch/lm.php?url=1000,43,4,20070117103715-FR/Dufaux_Alain_-_Automatic_sound_detection_and_recognition_20070117.pdf"><b>PDF
example.</b></a>"""

    
    def get(self, environ, start_response):
        """ Callback method for new http request.
        
        """
        #get parameters from the URI
        (path, opts) = self.getParams(environ)

        #check if is valid
        self.logger.debug("Accessing: %s with opts: %s" % (path, opts))

        if re.search(r'document/render', path) is not None:
            self.logger.debug("Render file with opts: %s" % opts)
            if opts.has_key('url'):
                max_width = max_height = output_format = None
                page_nr = 1
                angle = 0
                if opts.has_key('max_height'):
                    max_height = int(opts['max_height'])
                if opts.has_key('max_width'):
                    max_width = int(opts['max_width'])
                if opts.has_key('angle'):
                    angle = int(opts['angle'])
                if opts.has_key('page_nr'):
                    page_nr = int(opts['page_nr'])
                (mime_type, data) = self.render(url=opts['url'],
                        max_output_size=(max_width, max_height), angle=angle,
                        index={'page_number':page_nr}, output_format=output_format)
                start_response('200 OK', [('content-type',
                    mime_type),('content-length', str(len(data)))])
                return [data]
            else:
                raise ApplicationError.InvalidArgument('Invalid Argument')

    def _chooseProcessor(self, file_name, mime):

        if re.match('.*?/pdf.*?', mime):
            self.logger.debug("Pdf processor found!")
            pdf = PdfProcessor(file_name)
            return pdf
        
        if re.match('image/.*?', mime):
            self.logger.debug("Image processor found!")
            return ImageProcessor(file_name)
        self.logger.debug("Cannot process file with %s mime type." % mime)
        raise ApplicationError.UnsupportedFormat("Cannot process file with %s mime type." % mime)

    def render(self, url, max_output_size=None, angle=0, index=None, output_format=None):
        (file_name, mime) = self.getRemoteFile(url)
            
        #check the mime type
        self.logger.debug("Url: %s Detected Mime: %s" % (url, mime))
        processor = self._chooseProcessor(file_name, mime)
        return processor.render(max_output_size, angle, index, output_format)

    def getParams(self, environ):
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
        self.logger.debug("To parse: %s" % to_parse)
        if len(to_parse) > 0:
            res = list(re.match(r'(.*?)&{0,1}url=(.*)', to_parse).groups())
            #print res.groups()
            #replace all until the first occurence of url=
            opts['url'] = res.pop()
            if len(res) > 0:
                for v in res:
                    args = v.split('&')
                    for a in args:
                        res_args = list(re.match(r'(.*?)=(.*)', a).groups())
                        opts[res_args[0]] = res_args[1]
                    
        return (path, opts)

            
    
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
    application = DocProcessorApp()
    server = make_server('', options.port, application)
    server.serve_forever()

if __name__ == '__main__':
    main()

