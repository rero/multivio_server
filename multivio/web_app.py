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
import time
import logging

from mvo_config import MVOConfig

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
            '14' : 'rameau_de_sapin',
            '15' : 'l_express',
            '16' : 'l_impartial'
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

class WebApplication(object):
    def __init__(self, temp_dir=MVOConfig.General.temp_dir):
        self.usage = """<br><h1>Welcome to the multivio server.</h1>
        This is an abstract base class. Do not use it!
"""
        self._tmp_dir = temp_dir
        self._tmp_files = []
	#import socket
	#socket.setdefaulttimeout(1)
        self._urlopener = urllib.FancyURLopener()
        self._urlopener.version = MVOConfig.Url.user_agent
        self.logger = logging.getLogger(MVOConfig.Logger.name + "."
                        + self.__class__.__name__) 

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
        self.logger.debug('Temp dir: %s' % self._tmp_dir)
        local_file = os.path.join(self._tmp_dir, url_md5)

	#file in the local file system
        if url.startswith("file://"):
            mime = 'image/jpeg'
            local_file = url.replace('file://','')
            return (local_file, mime)
	
	#file in RERO DOC nfs volume
	rero_local_file = self.lm(url)
	if rero_local_file is not None and os.path.isfile(rero_local_file):
	    local_file = rero_local_file
            self.logger.debug("File: %s" % local_file)
	    mime = "application/pdf"
	    if re.match(".*?\.(jpg|jpeg)", rero_local_file):
		mime = "image/jpeg"
	    if re.match(".*?\.png", rero_local_file):
		mime = "image/png"
	    if re.match(".*?\.gif", rero_local_file):
		mime = "image/gif"
	    return (local_file, mime)
	
	#remote file
        lock_file = local_file + ".lock"
	mime_file = local_file + ".mime"

	#already downloaded?
        if not os.path.isfile(local_file):
            if not os.path.isfile(lock_file):
                self.logger.debug("Create lock file: %s" % lock_file)
                open(lock_file, 'w').close() 
                self.logger.debug("Try to retrieve %s file" % url)
        	try:
                    (filename, headers) = self._urlopener.retrieve(url)
        	except Exception:
                    os.remove(lock_file)
            	    raise ApplicationError.InvalidURL("Invalid URL: %s" % url)
		mime = headers['Content-Type']
		if re.match('.*?/x-download', mime):
		    mime = 'application/pdf'
                shutil.move(filename, local_file)
                self._tmp_files.append(local_file)
                os.remove(lock_file)
                self.logger.debug("Remove: %s" % lock_file)
		output_mime_file = file(mime_file, "w")
		output_mime_file.write(mime)
		output_mime_file.close()

	    #downloading by an other process?
            else:
                while os.path.isfile(lock_file):
                    self.logger.debug("Wait for file %s" % lock_file)
                    time.sleep(.2)
	output_mime_file = file(mime_file, "r")
	mime = output_mime_file.read()
	output_mime_file.close()
	self.logger.debug("Url: %s Mime: %s LocalFile: %s" % (url, mime,
                local_file))
        if re.match('.*?/pdf.*?', mime) or \
      	    re.match('.*?/xml.*?', mime) or \
      	    re.match('image/.*?', mime):
            return (local_file, mime)
	else:
	    return (None, mime)


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


