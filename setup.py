#!/usr/bin/env python
from distutils.core import setup, Extension

poppler_install_path = '/usr/local'
import multivio

setup(
    name='multivio',
    version=multivio.__version__,
    description='Multivio server.',
    long_description='''Multivio is a project...''',
    license=multivio.__license__,
    url='http://www.multivio.org',
    ext_modules=[Extension('multivio/poppler/_mypoppler', ['multivio/poppler/mypoppler.i'],
        swig_opts=['-c++', '-modern', '-I%s/include' % poppler_install_path],
        extra_compile_args=['-I%s/include/poppler' % poppler_install_path],
        extra_link_args=['-lpoppler'])], 
    py_modules=['multivio.poppler.mypoppler'],
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
    install_requires=[
        "Pillow==3.0.0"
    ]
)
