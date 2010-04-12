#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


import logging

class MVOConfig:

    class General:
        temp_dir = '/var/www/multivio/temp' 
        lib_dir = '/var/www/multivio/lib/python'
        sys_pathes = ['/var/www/multivio/lib/python',
                '/var/www/mutlivio/bin']

    class Url:
        user_agent = 'Firefox/3.5.2'

    class Logger:
        name = "multivio"
        file_name = "/tmp/multivio.log"
        console = True
        level = logging.DEBUG
        
        											
        											
        
        											
