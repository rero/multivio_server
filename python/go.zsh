
swig -I/usr/include -c++ -python pdf.i
g++ -g -fPIC -c pdf_wrap.cxx -I/usr/include/poppler -I/usr/include/python2.5  -I/usr/include/freetype2
g++ -g -shared pdf_wrap.o -L/usr/lib -lpoppler -lfreetype -o _mypoppler.so  -lpython2.5
