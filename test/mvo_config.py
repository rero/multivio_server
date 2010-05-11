#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


import logging

class MVOConfig:

    class General:
        temp_dir = '/tmp' 

    class Url:
        user_agent = 'Firefox/3.5.2'

    class Logger:
        name = "multivio"
        file_name = "./multivio.log"
        console = True
        level = logging.DEBUG
        
        											
        											
        
        											
