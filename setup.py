#!/usr/bin/env python
from distutils.core import setup, Extension

poppler_install_path = '/usr'

setup(
    name='multivio',
    version='0.0.1b',
    description='Multivio server.',
    long_description='''Multivio is a project...''',
    license='Internal',
    author='Johnny Mariethoz',
    author_email='Johnny do Mariethoz at rero do ch',
    url='http://www.multivio.org',
    ext_modules=[Extension('multivio/_mypoppler', ['multivio/mypoppler.i'],
        swig_opts=['-c++', '-modern', '-I%s/include' % poppler_install_path],
        extra_compile_args=['-I%s/include/poppler' % poppler_install_path],
        extra_link_args=['-lpoppler'])], 
    py_modules=['multivio/mypoppler'],
    packages=[
    'multivio'
    ],
    scripts=[
    'tools/multivio_server.py', 'tools/mvo_config_example.py'
    ],
    keywords=['multivio'],
    classifiers=[
    'Development Status :: Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: Internal',
    ],
    )
