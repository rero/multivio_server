#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
import sys
import os
import cStringIO
from optparse import OptionParser
import urllib
import cgi
import re
from application import Application

import Image
import cairo
import poppler


# local modules
class DocumentError:
    class InvalidUrl(Exception):
        pass

class DocumentApp(Application):
    def __init__(self):
        Application.__init__(self)
        self.usage = """Using the GET method it return a thumbnail in PNG format of a given size for a given
image.<br>
<b>Arguments:</b>
<ul>
<li><em>url --string--</em>  url of an image file.
<li><em>width --integer--</em>  max width of the output image in pixel. Default(400)
<li><em>pagenr --integer--</em>  extract the page <pagenr>. Pdf only. Default(1).
</ul>
<a
href="/multivio/document/get?width=400&url=http://doc.rero.ch/lm.php?url=1000,10,2,20080701134109-FH/Braune_MWK_tab1a.jpg"><b>Image
example.</b></a><br>
<a
href="/multivio/document/get?width=800&pagenr=2&url=http://doc.rero.ch/lm.php?url=1000,43,4,20070117103715-FR/Dufaux_Alain_-_Automatic_sound_detection_and_recognition_20070117.pdf"><b>PDF
example.</b></a>"""
    
    def get(self, environ, start_response):
        (path, opts) = self.getParams(environ)
        print environ
        if opts.has_key('url'):
            width = 400
            url = urllib.unquote(opts['url'][0])
            if opts.has_key('width'):
                width = int(opts['width'][0])
            (image_file, mime) = self.getRemoteFile(url)
            if re.match('image/', mime):
                (header, content) = self.resize(image_file, width)
                start_response('200 OK', header)
                return [content]
            if re.match('application/pdf', mime):
                pagenr = 1
                if opts.has_key('pagenr'):
                    pagenr = int(opts['pagenr'][0])
                (header, content) = self.getImageFromPdf(image_file, pagenr, width)
                start_response('200 OK', header)
                return [content]
            start_response('400 Bad Request', [('content-type', 'text/html')])
            return ['Bad input format']
        else:
            start_response('400 Bad Request', [('content-type', 'text/html')])
            return ["Missing url options."]

    def getImageFromPdf(self, filename, pagenr=1, width=400):
        doc = poppler.document_new_from_file('file://'+filename, None)
        page    = doc.get_page(pagenr)
        x, y    = page.get_size()
        height = int(width*y/x)
        #x, y    = page.set_size(width, height)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(x),
            int(y))
        ctx = cairo.Context(surf)
        page.render(ctx)
        
        pil = Image.frombuffer("RGBA", (surf.get_width(), surf.get_height()), surf.get_data(), "raw", "BGRA", 0, 1)
        #pil.thumbnail((width, height), Image.ANTIALIAS)
        pil = pil.resize((width, height), Image.BICUBIC)
        f = cStringIO.StringIO()
        pil.save(f, "PNG")
        f.seek(0)
        content = f.read()
        header = [('content-type', 'image/png'), ('content-length',
        str(len(content)))]
        return(header, content)
    
    
    def resize(self, file_name, width=100):
        width = int(width)
        img = Image.open(file_name)
        img.thumbnail((width, width), Image.ANTIALIAS)
        f = cStringIO.StringIO()
        img.save(f, "PNG")
        f.seek(0)
        content = f.read()
        header = [('content-type', 'image/png'), ('content-length',
        str(len(content)))]
        return(header, content)


application = DocumentApp()

#---------------------------- Main Part ---------------------------------------

if __name__ == '__main__':

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Change It")



    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)

    parser.add_option ("-p", "--port", dest="port",
                       help="Http Port (Default: 4041)",
                       type="int", default=4041)


    (options,args) = parser.parse_args ()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")
    from wsgiref.simple_server import make_server
    server = make_server('', options.port, application)
    server.serve_forever()


