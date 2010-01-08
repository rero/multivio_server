
swig -I/home/marietho/temp/poppler-install/include -c++ -python pdf.i
g++ -g -fPIC -c pdf_wrap.cxx -I/home/marietho/temp/poppler-install/include/poppler -I/usr/include/python2.5  -I/usr/include/freetype2
g++ -g -shared pdf_wrap.o -L/home/marietho/temp/poppler-install/lib -lpoppler -lpoppler-glib -lcairo -lfreetype -o _mypoppler.so
