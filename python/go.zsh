
swig -I/usr/local/include -c++ -python pdf.i
g++ -g -fPIC -c pdf_wrap.cxx -I/usr/local/include/poppler -I/usr/include/python2.6  -I/usr/include/freetype2
g++ -g -shared pdf_wrap.o -L/usr/local/lib -lpoppler -lfreetype -o _mypoppler.so -lpython
