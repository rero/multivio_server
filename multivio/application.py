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
import shutil

from wsgiref.util import setup_testing_defaults
document_type = {
            '10' : 'book',
            '20' : 'journal', 
            '25' : 'newspaper',
            '30' : 'picture', 
            '40' : 'thesis',
            '41' : 'dissertation',
            '42' : 'preprint',
            '43' : 'postprint',
            '44' : 'report',
            '15' : 'partition'
            }
localisations = {
            '1'  : 'rero',
            '2'  : 'unifr',
            '3'  : 'unige',
            '4'  : 'unine',
            '5'  : 'unil',
            '6'  : 'unisi',
            '8'  : 'hetsfr',
            '9'  : 'hegge',
            '10' : 'ecav',
            '11' : 'hevs2',
            '12' : 'hepvs',
            '13' : 'iukb',
            '14' : 'idiap',
            '15' : 'fsch',
            '16' : 'cred',
            '17' : 'curpufm',
            '18' : 'crem',
            '19' : 'medvs',
            '20' : 'crepa',
            '21' : 'ffhs',
            '22' : 'hevs_',
            '23' : 'bpuge',
            '24' : 'hetsge',
            '25' : 'baage',
            '26' : 'elsvd',
            '28' : 'hedsfr',
            '29' : 'bvcfne',
            '30' : 'coege',
            '31' : 'mhnge',
            '32' : 'bpune',
            '33' : 'bcufr',
            '34' : 'bmuge',
            '35' : 'imvge',
            '36' : 'aege',
            '37' : 'avlvd',
            '38' : 'cio',
            '39' : 'pa16ju',
            '40' : 'iheid'
            }
book_collections = {
            '10' : 'chronique_fribourgeoise'
}

journal_collections = {
            '4'  : 'cahiers_de_psychologie',
            '5'  : 'dossiers_de_psychologie',
            '6'  : 'droit_du_bail',
            '7'  : 'revue_suisse_droit_sante',
            '10' : 'bulletin_vals_asla',
	    '13' : 'revue_tranel'
}
            
newspaper_collections = {
            '1'  : 'la_liberte',
            '2'  : 'freiburger_nachrichten',
            '8'  : 'la_pilule',
            '9'  : 'le_cretin_des_alpes',
            '11' : 'messager_boiteux_neuchatel',
            '12' : 'revue_historique_neuchateloise',
            '13' : 'etrennes_fribourgeoises',
            '14' : 'rameau_de_sapin'
}


class ApplicationError:
    """Base class for errors in the Urn packages."""
    class InvalidURL(Exception):
        """The configuration is not valid."""
        pass
    class PermissionDenied(Exception):
	pass

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
        try:
            mime = urllib.urlopen(url).info()['Content-Type']
        except Exception:
            raise ApplicationError.InvalidURL("Invalid URL: %s" % url)
        print "Mime: %s" % mime
        if re.match('.*?/pdf.*?', mime):
            local_file = local_file+'.pdf'
        if re.match('.*?/png.*?', mime):
            local_file = local_file+'.png'
        if re.match('.*?/jpeg.*?', mime):
            local_file = local_file+'.jpg'
        if re.match('.*?/xml*?', mime):
            local_file = local_file+'.xml'
        lock_file = local_file+".lock"
	rero_local_file = self.lm(url)
	if rero_local_file is not None and os.path.isfile(rero_local_file):
	    local_file = rero_local_file
            print "File: %s" % local_file
        else:
            if not os.path.isfile(local_file):
                if not os.path.isfile(lock_file):
                    print "Create: ", lock_file
                    open(lock_file, 'w').close() 
                    (filename, headers) = urllib.urlretrieve(url)
                    shutil.move(filename, local_file)
                    self._tmp_files.append(local_file)
                    os.remove(lock_file)
                    print "Remove: ", lock_file
                else:
                    while os.path.isfile(lock_file):
                        "Wait for file"
                        time.sleep(.2)
        return (local_file, mime)

    def lm(self, url):
        if re.match('http://doc.rero.ch/lm.php', url):
            parts = url.split(',')
            if parts[0].endswith('1000'):
                doc_type = document_type[parts[1]]
                if doc_type == 'journal':
                    collection = journal_collections[parts[2]]
                elif doc_type == 'newspaper':
                    collection = newspaper_collections[parts[2]]
                else:
                    collection = localisations[parts[2]]
                return '/rerodoc/public/%s/%s/%s' % (doc_type, collection, parts[3])
    	else:
                raise ApplicationError.PermissionDenied("Your are not allowed to see this document.")
        return None

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
    application = Application()
    server = make_server('', options.port, application)
    server.serve_forever()


