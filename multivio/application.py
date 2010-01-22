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
from optparse import OptionParser
import cgi
import re
import hashlib
import urllib

from wsgiref.util import setup_testing_defaults

class InputProcessed(object):
    def read(self, *args):
        raise EOFError('The wsgi.input stream has already been consumed')
    readline = readlines = __iter__ = read

class Application(object):
    def __init__(self, temp_dir=None):
        self.usage = """<br><h1>Welcome to the multivio server.</h1>
<h2>Available pathes:</h2>
    <h3>/multivio/document/get?url=</h3>
        Using the GET method it return a CDM in json format.<br>
        <b>Arguments:</b>
        <ul>
        <li><em>url --string--</em>  url of a xml file representing the record.
        </ul>
        <a
        href="/multivio/document/get?url=http://doc.rero.ch/record/9264/export/xd?"><b>RERODOC
        example.</b></a>
    <h3>/multivio/log</h3>
        Using the POST method it put a log message in the server.<br>
    <h3>/multivio/document/thumbnail?size=400&url=</h3>
        Using the GET method it return a thumbnail in PNG format of a given size for a given
        image.<br>
        <b>Arguments:</b>
        <ul>
        <li><em>url --string--</em>  url of an image file.
        <li><em>size --integer--</em>  size of the output image in pixel.
        </ul>
        <a
        <a
        href="/multivio/document/thumbnail?size=400&url=http://doc.rero.ch/lm.php?url=1000,10,2,20080701134109-FH/Braune_MWK_tab1a.jpg"><b>Thumbnail
        example.</b></a>
    <h3>/multivio/document/pdf?zoom=1&pagenr=1&url=</h3>
        Using the GET method it return a PNG image corresponding to the pagenr
        of pdf document for a given zoom factor.<br>
        <ul>
        <li><em>url --string--</em>  url of a pdf file.
        <li><em>zoom --real--</em>  zoom factor for the output image file.
        <li><em>pagenr --integer--</em>  page number of the input pdf file to
        convert.
        </ul>
        <a
        href="/multivio/document/pdf?pagenr=1&zoom=2&url=http://doc.rero.ch/lm.php?url=1000,43,2,20091211165357-BU/shalkevitch_rfg.pdf"><b>PDF
        example.</b></a>
    <h3>/multivio/document/html?zoom=1&pagenr=1&url=</h3>
        Using the GET method it return a html document corresponding to the pagenr
        of pdf document for a given zoom factor.<br>
        <ul>
        <li><em>url --string--</em>  url of a pdf file.
        <li><em>zoom --real--</em>  zoom factor for the output image file.
        <li><em>pagenr --integer--</em>  page number of the input pdf file to
        convert.
        </ul>
        <a href="/multivio/document/html?pagenr=1&zoom=2&url=http://doc.rero.ch/lm.php?url=1000,43,2,20091211165357-BU/shalkevitch_rfg.pdf"><b>HTML
        example.</b></a>
"""
	if temp_dir is not None:
            self._tmp_dir = temp_dir
	else:
            self._tmp_dir = '/tmp'
        self._tmp_files = []

    def get(self, environ, start_response):
        start_response('405 Method Not Allowed', [('content-type',
                        'text/html')])
        return ["GET is not allowed."]

    def post(self, environ, start_response):
        post_form = self.getPostForm(environ)
        start_response('405 Method Not Allowed', [('content-type',
                        'text/html')])
        return ["POST is not allowed."]
    
    def getParams(self, environ):
        path = environ['PATH_INFO']
        opts = cgi.parse_qs(environ['QUERY_STRING'])
        return (path, opts)

    def __call__(self, environ, start_response):

        if re.match('.*?help.*?', environ['PATH_INFO']):
            start_response('200 OK', [('content-type', 'text/html')])
            return [self.usage]
            
        if environ['REQUEST_METHOD'].upper() == 'GET':
            return self.get( environ, start_response)

        if environ['REQUEST_METHOD'].upper() == 'POST':
            return self.post( environ, start_response)

        start_response('405 Method Not Allowed', [('content-type',
                        'text/html')])
        return ["%s is not allowed." % environ['REQUEST_METHOD'].upper()]

    def getRemoteFile(self, url):
        url_md5 = hashlib.sha224(url).hexdigest()
        local_file = os.path.join(self._tmp_dir, url_md5)
        mime = urllib.urlopen(url).info()['Content-Type']
        if mime == '.*?/pdf.*?':
            local_file = local_file+'.pdf'
        if re.match('.*?/xml*?', mime):
            local_file = local_file+'.xml'
        if not os.path.isfile(local_file):
            (filename, headers) = urllib.urlretrieve(url, local_file)
            self._tmp_files.append(filename)
        return (local_file, mime)

    def cleanTmpFiles(self):
        for f in self._tmp_files:
            os.remove(f)

    def getPostForm(self, environ):
        input = environ['wsgi.input']
        post_form = environ.get('wsgi.post_form')
        if (post_form is not None
            and post_form[0] is input):
            return post_form[2]
        fs = cgi.FieldStorage(fp=input,
                              environ=environ,
                              keep_blank_values=1)
        new_input = InputProcessed()
        post_form = (new_input, input, fs)
        environ['wsgi.post_form'] = post_form
        environ['wsgi.input'] = new_input
        return fs

application = Application()

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


