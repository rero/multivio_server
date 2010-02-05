#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"



class MVOConfig:

    class General:
        temp_dir = '/var/www/multivio/temp' 

    class Url:
        user_agent = 'Firefox/3.5.2'

    class Info:
        font_name = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf"
        font_size = 25
        bg_color = (65, 65, 65)
        fg_color = (255, 255, 255)
        output_size = (1060, 1500)
        output_dir = '/var/www/multivio/images'
        #output_dir = '/var/www/multivio/images'
        url = 'file:///var/www/multivio/images'
        
        											
        											
        
        											
