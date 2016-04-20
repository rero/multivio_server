#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Apache config file for Multivio server."""

#==============================================================================
#  This file is part of the Multivio software.
#  Project  : Multivio - https://www.multivio.org/
#  Copyright: (c) 2009-2011 RERO (http://www.rero.ch/)
#  License  : See file COPYING
#==============================================================================


import logging

class MVOConfig:

    class General:
        temp_dir = '/var/tmp/multivio'
        lib_dir = ''
        sys_pathes = []

    class Url:
        user_agent = 'Firefox/3.5.2'
        timeout = 120 #2 minutes

    class Logger:
        name = "multivio"
        file_name = "/var/log/multivio/multivio.log"
        console = False
        level = logging.INFO
