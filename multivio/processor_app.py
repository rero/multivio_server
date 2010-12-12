#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Document Parser module for Multivio"""

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules ---------------------------------------

# import of standard modules
from optparse import OptionParser
import re
import sys
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

# local modules
from mvo_config import MVOConfig
from web_app import WebApplication

from pdf_processor import PdfProcessor
from image_processor import ImageProcessor
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

        self.usage = """<h4>render</h4>Using the GET method it return a thumbnail in PNG format of a given size for a given
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
example.</b></a>

<h4>search</h4>Search a PDF file and return results in a dictionary structure.<br>
<b>Arguments:</b>
<ul>
<li><em>url --string--</em>  url of a pdf file. Required.
<li><em>query --string--</em>  text to find in the document. Required.
<li><em>from --integer--</em> start the search at page from. Default(1).
<li><em>to --integer--</em> end the search at page to. Default(&lt;number_of_pages&gt;).
<li><em>max_results --integer--</em> limit the number of the returned results. Default(50).
<li><em>context_size --integer--</em> approximate number of characters of context around found words (left & right).
Default(0).
<li><em>angle --integer--</em> angle of display in degrees. Default(0).
</ul>
<a
href="/server/document/search?query=test&angle=0&max_results=15&context_size=10&url=http://doc.rero.ch/lm.php?url=1000,43,2,20100916082754-BW/cel_mas.pdf"><b>Search example.</b></a><br>

<h4>get_text</h4>Return the text contained inside the selected area.<br>
<b>Arguments:</b>
<ul>
<li><em>url --string--</em>  url of a pdf file. Required.
<li><em>page_nr --integer--</em> Number of the page to get text from. Default(1).
<li><em>x1 --integer--</em> x-coordinate of upper-left point of selected area. Default(0).
<li><em>y1 --integer--</em> y-coordinate of upper-left point of selected area. Default(0).
<li><em>x2 --integer--</em> x-coordinate of bottom-right point of selected area. Default(0).
<li><em>y2 --integer--</em> y-coordinate of bottom-right point of selected area. Default(0).
</ul>
<a href="/server/document/get_text?page_nr=68&x1=395&y1=347&x2=600&y2=358&url=http://doc.rero.ch/lm.php?url=1000,10,38,20100803165622-EB/2008_-_Rapport_du_groupe_de_travail_du_cio_pour_acceptation_des_candidatures_-_fre.pdf"><b>Get text example.</b></a>

<h4>get_indexing</h4>Returns index of a range of pages of the document.<br>
If a range of pages is specified with 'from' and 'to', 'page_nr' is ignored. Else, page number is used.<br/>
<b>Arguments:</b>
<ul>
<li><em>url --string--</em>  url of a pdf file. Required.
<li><em>page_nr --integer--</em> Number of the page to get the indexing from. Default(1).
<li><em>from --integer--</em> start page to get indexing of a range of pages. Default(1).
<li><em>to --integer--</em> end page to get indexing of a range of pages. Default(&lt;number_of_pages&gt;).
</ul>
<a href="/server/document/get_indexing?page_nr=1&url=http://doc.rero.ch/lm.php?url=1000,10,38,20100803165622-EB/2008_-_Rapport_du_groupe_de_travail_du_cio_pour_acceptation_des_candidatures_-_fre.pdf"><b>Example with a page.</b></a><br/>
<a href="/server/document/get_indexing?from=3&to=6&url=http://doc.rero.ch/lm.php?url=1000,10,38,20100803165622-EB/2008_-_Rapport_du_groupe_de_travail_du_cio_pour_acceptation_des_candidatures_-_fre.pdf"><b>Example with a range of pages.</b></a>

"""

    
    def get(self, environ, start_response):
        """ Callback method for new http request.
        
        """
        #get parameters from the URI
        (path, opts) = self.get_params(environ)

        #check if is valid
        self.logger.info("Accessing: %s with opts: %s" % (path, opts))
        self.logger.debug("Cookie: %s" % self.cookies)

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
        if re.search(r'document/get_size', path) is not None:
            self.logger.debug("Get file size with opts: %s" % opts)
            if opts.has_key('url'):
                page_nr = 1
                if opts.has_key('page_nr'):
                    page_nr = int(opts['page_nr'])
                size = self.get_size(url=opts['url'],
                    index={'page_number':page_nr})
                start_response('200 OK', [('content-type',
                    'application/json')])
                return [json.dumps(size, sort_keys=True, indent=2)]
            else:
                raise ApplicationError.InvalidArgument('Invalid Argument')

        if re.search(r'document/get_text', path) is not None:
            self.logger.debug("Get text with opts: %s" % opts)
            if opts.has_key('url'):
                page_nr = 1
                # round coordinates to 2 decimals
                x1 = x2 = y1 = y2 = angle = 0

                if opts.has_key('page_nr'):
                    page_nr = int(opts['page_nr'] or 1)
                if opts.has_key('x1'):
                    x1 = round(float(opts['x1']), 2)
                if opts.has_key('x2'):
                    x2 = round(float(opts['x2']), 2) 
                if opts.has_key('y1'):
                    y1 = round(float(opts['y1']), 2) 
                if opts.has_key('y2'):
                    y2 = round(float(opts['y2']), 2)
                if opts.has_key('angle'):
                    angle = int(opts['angle'] or 0)

                text_result = self.get_text(url=opts['url'],
                    index={'page_number':page_nr, 'bounding_box':{'x1':x1,'x2':x2,'y1':y1,'y2':y2}}, angle=angle)
                # get_text now takes rotation angle into account
                start_response('200 OK', [('content-type',
                    'application/json')])
                return [json.dumps(text_result, sort_keys=True, indent=2)]
            else:
                raise ApplicationError.InvalidArgument('Invalid Argument')

        if re.search(r'document/get_indexing', path) is not None:
            self.logger.debug("Get page index with opts: %s" % opts)
            if opts.has_key('url'):
                page_nr = from_ = to_ = None
                if opts.has_key('page_nr'):
                    page_nr = int(opts['page_nr'] or 1)
                if opts.has_key('from'):
                    from_ = int(opts['from'] or 0)
                if opts.has_key('to'):
                    to_ = int(opts['to'] or 0)

                pages_index = self.get_indexing(url=opts['url'],
                    index={'page_number':page_nr}, from_=from_, to_=to_)
                start_response('200 OK', [('content-type',
                    'application/json')])
                return [json.dumps(pages_index, sort_keys=False, indent=2)]
            else:
                raise ApplicationError.InvalidArgument('Invalid Argument')

        if re.search(r'document/search', path) is not None:
            self.logger.debug("Search document with opts: %s" % opts)
            if opts.has_key('url'):
                if not opts.has_key('query'):
                    raise ApplicationError.InvalidArgument('Invalid Argument: "\
                            "param query missing')

                # note: unquote query string, useful for getting right
                # accents and special chars
                url = opts['url']
                import urllib
                query = urllib.unquote(opts['query'])
                from_ = 1
                to_ = max_results = sort = context_size = None
                angle = 0                

                if opts.has_key('from'):
                    from_ = int(opts['from'] or 0)
                if opts.has_key('to'):
                    to_ = int(opts['to'] or 0)
                if opts.has_key('max_results'):
                    max_results = int(opts['max_results'] or 0)
                if opts.has_key('sort'):
                    sort = int(opts['sort'] or 0)
                if opts.has_key('context_size'):
                    context_size = int(opts['context_size'] or 0)
                if opts.has_key('angle'):
                    angle = int(opts['angle'] or 0)
                # get results
                results = self.search(url, query, from_, to_, max_results,
                    sort, context_size, angle)
                # add url to 'file_position' of results
                results['file_position']['url'] = url
                start_response('200 OK', [('content-type',
                    'application/json')])
                return [json.dumps(results, sort_keys=False, indent=2,
                    encoding='utf-8')]
            else:
                raise ApplicationError.InvalidArgument('Invalid Argument')


    def _choose_processor(self, file_name, mime):
        """Select the right processor given the mime type."""

        if re.match('.*?/pdf.*?', mime):
            self.logger.info("Pdf processor found!")
            pdf = PdfProcessor(file_name)
            return pdf
        
        if re.match('image/.*?', mime):
            self.logger.info("Image processor found!")
            return ImageProcessor(file_name)
        self.logger.error("Cannot process file with %s mime type." % mime)
        raise ApplicationError.UnsupportedFormat(
            "Cannot process file with %s mime type." % mime)

    def render(self, url, max_output_size=None, angle=0, 
        index=None, output_format=None):
        """Generate a content to display for a given document."""
        restricted_document = False
        try:
            (file_name, mime) = self.get_remote_file(url)
        except ApplicationError.PermissionDenied:
            (file_name, mime) = self.get_remote_file(url, force=True)
            restricted_document = True
            
        #check the mime type
        processor = self._choose_processor(file_name, mime)
        return processor.render(max_output_size, angle, index, output_format,
                restricted_document)

    def get_size(self, url, index=None):
        """Generate a content to display for a given document."""
        (file_name, mime) = self.get_remote_file(url)
            
        #check the mime type
        processor = self._choose_processor(file_name, mime)
        return processor.get_size(index)

    def get_text(self, url, index=None, angle=0):
        """Get the text in the selected zone in the document"""
        (file_name, mime) = self.get_remote_file(url)

        #check the mime type
        processor = self._choose_processor(file_name, mime)
        return processor.get_text(index, angle)

    def get_indexing(self, url, index=None, from_=None, to_=None):
        """Get index of the positions of words on a given page"""
        (file_name, mime) = self.get_remote_file(url)

        #check the mime type
        processor = self._choose_processor(file_name, mime)
        return processor.get_indexing(index, from_, to_)

    def search(self, url, query, from_=None, to_=None, max_results=None,
            sort=None, context_size=None, angle=0):
        """Search text in a document"""
        (file_name, mime) = self.get_remote_file(url)

        #check the mime type
        processor = self._choose_processor(file_name, mime)
        return processor.search(query, from_, to_, max_results, sort,
                context_size, angle)

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
        self.logger.debug("To parse: %s" % to_parse)
        if len(to_parse) > 0:
            res = list(re.match(r'(.*?)&{0,1}url=(.*)', to_parse).groups())
            #replace all until the first occurence of url=
            opts['url'] = res.pop()
            if len(res) > 0 and len(res[0]) > 0:
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

