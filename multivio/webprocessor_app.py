#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Logging module for the Multivio application."""

#==============================================================================
#  This file is part of the Multivio software.
#  Project  : Multivio - https://www.multivio.org/
#  Copyright: (c) 2009-2011 RERO (http://www.rero.ch/)
#  License  : See file COPYING
#==============================================================================

__copyright__ = "Copyright (c) 2009-2011 RERO"
__license__ = "GPL V.2"

#---------------------------- Modules -----------------------------------------

# import of standard modules
from optparse import OptionParser
import re
import os
import sys
import time
import cStringIO
import hashlib
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

try:
    import Image
except:
    from PIL import Image
WKHTMLTOX_SUPPORT = True
try:
    import wkhtmltox
except ImportError:
    WKHTMLTOX_SUPPORT = False

# local modules
from web_app import WebApplication, ApplicationError, WebException


class WebProcessorError:
    """Prefix to import all exceptions."""

    class UnableToRenderWebPage(WebException):
        """Problem with the remote server.
            HTTP: 502
        """
        def __init__(self, value=None):
            WebException.__init__(self, value)
            self.http_code = "502 Bad Gateway"

#---------------------------- Classes -----------------------------------------

class WebProcessorApp(WebApplication):
    """Web application for logging"""
    def __init__(self):
        """Basic constructor"""
        WebApplication.__init__(self)
        self.usage = """Create a image as the reder of a website.
<b>Arguments:</b>
<ul>
<li><em>max_width --integer--</em>  max width of the output image in pixel.  Default(None)
<li><em>max_height --integer--</em>  max height of the output image in pixel.  Default(None)
<li><em>url --string--</em>  url of an image file.
</ul>
<a
href="/server/website/render?max_width=400&max_height=400&url=http://doc.rero.ch"><b>Example
of redering RERO DOC web site.</b></a><br>
<br>"""
    
    def get(self, environ, start_response):
        """ Callback method for new http request.
        
        """
        if not WKHTMLTOX_SUPPORT:
            raise WebProcessorError.UnableToRenderWebPage("WKTHMLTOX not installed")
        #get parameters from the URI
        (path, opts) = self.get_params(environ)

        #check if is valid
        max_width  = max_height = 1024
        try:
            max_width = int(opts['max_width'])
        except KeyError:
            pass
        try:
            max_height = int(opts['max_height'])
        except KeyError:
            pass
        if re.search(r'render', path) is not None and  opts.has_key('url'):
            url_to_fetch = opts['url']
            url_md5 = hashlib.sha224(url_to_fetch).hexdigest()
            local_file = os.path.join(self._tmp_dir, url_md5+".jpg")

            to_download = False
            try:
                #file exists: ATOMIC?
                os.open(local_file, os.O_CREAT|os.O_EXCL|os.O_RDWR)
                to_download = True
            except Exception:
                pass

            if to_download:
                self.logger.debug("Try to retrieve %s file" % url_to_fetch)
                filename = os.path.join(self._tmp_dir, url_md5+"_tmp.jpg")
                start = time.time()
                try:
                    self._render_url(url_to_fetch, filename)
                except Exception, e:
                    os.remove(filename)
                    raise WebProcessorError.UnableToRenderWebPage(str(e))
                
                #file in cache
                os.rename(filename, local_file)
            else:
                #downloading by an other process?
                start_time_wait = time.time() 
                time_out_counter = 0
                while os.path.getsize(local_file) == 0L \
                    and time_out_counter < self._timeout:
                    self.logger.info("Wait for file: %s" % local_file )
                    time.sleep(.5)
                    time_out_counter = time.time() - start_time_wait
                if time_out_counter >= self._timeout:
                    self.logger.warn("Rendering process timeout")
                    raise WebProcessorError.UnableToRenderWebPage(
                        "Rendering process timeout: %s" % url_to_fetch)

            data = self._resize(local_file, max_width, max_height)
            start_response('200 OK', [('content-type',
                'image/jpeg'),('content-length',
                                    str(len(data)))])
            return [data]

        raise ApplicationError.InvalidArgument("Invalid Argument")

    def _resize(self, file_name, max_width, max_height):
            img = Image.open(file_name)
            img.thumbnail((max_width, max_height), Image.ANTIALIAS)
            temp_file = cStringIO.StringIO()
            img.save(temp_file, "JPEG", quality=90)
            temp_file.seek(0)
            data = temp_file.read()
            return data

    def _render_url(self, url, output_file_name):
            img = wkhtmltox.Image()
            img.set_global_setting('screenHeight', '1024')
            img.set_global_setting('out', output_file_name)
            img.set_global_setting('in', url)
            img.convert()
    
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
    application = WebProcessorApp()
    server = make_server('', options.port, application)
    server.serve_forever()

if __name__ == '__main__':
    main()
