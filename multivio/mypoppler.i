
%module mypoppler
%{
#include "poppler-config.h"
#include "PDFDoc.h"
#include "goo/GooString.h"
#include "goo/gtypes.h"
#include "SplashOutputDev.h"
#include "GlobalParams.h"
#include "Catalog.h"
#include "OutputDev.h"
#include "Page.h"
#include "splash/SplashFontEngine.h"
#include "goo/gmem.h"
#include "goo/GooString.h"
#include "GlobalParams.h"
#include "PDFDoc.h"
#include "splash/SplashBitmap.h"
#include "splash/Splash.h"
#include "SplashOutputDev.h"
#include "TextOutputDev.h"
%}
%include "typemaps.i"

//for TextWord::getBBox()
%apply double *OUTPUT {double *xMinA, double *yMinA, double *xMaxA, double *yMaxA};
%apply double *OUTPUT {double *xMin, double *yMin, double *xMax, double *yMax};

enum SplashColorMode {
  splashModeMono1,    // 1 bit per component, 8 pixels per byte,
        //   MSbit is on the left
  splashModeMono8,    // 1 byte per component, 1 byte per pixel
  splashModeRGB8,   // 1 byte per component, 3 bytes per pixel:
        //   RGBRGB...
  splashModeBGR8,   // 1 byte per component, 3 bytes per pixel:
        //   BGRBGR...
  splashModeXBGR8   // 1 byte per component, 4 bytes per pixel:
        //   XBGRXBGR...
#if SPLASH_CMYK
  ,
  splashModeCMYK8   // 1 byte per component, 4 bytes per pixel:
        //   CMYKCMYK...
#endif
};
typedef bool GBool;
typedef unsigned char SplashColor[4];
%typemap(typecheck) (SplashColorPtr)
{
 $1 = PyTuple_Check($input);
}
%{
  void init()
  {
    globalParams = new GlobalParams();
  }
%}
void init();
%typemap(in) SplashColorPtr
{ 
  if (PyTuple_Check($input)) 
  { 
    //SplashColor temp;
    unsigned char* temp = (unsigned char*) malloc(3*sizeof(unsigned char));
    fflush(stdout);
    /*
    if (!PyArg_ParseTuple($input,"iii", & temp[0], & temp[1], &temp[2])) 
    { 
      PyErr_SetString(PyExc_TypeError,"tuple must consist of 4 integers"); 
        return NULL; 
    } 
    */
    temp[0] = 255;
    temp[1] = 255;
    temp[2] = 255;
    $1 = temp; 
  } 
  else 
  { 
    if (SWIG_ConvertPtr($input, (void **) &$1, $1_descriptor,   
          SWIG_POINTER_EXCEPTION) == -1) 
    { 
      PyErr_SetString (PyExc_TypeError,"expected a tuple"); 
      return NULL; 
    } 
  } 
} 
%typemap(out) SplashColorPtr
{
  //printf("Out\n");
  //fflush(stdout);
  $result = PyString_FromStringAndSize((char*) $1, 3*arg1->getWidth()*arg1->getHeight());
}

/************* GooString **************/

%typecheck (SWIG_TYPECHECK_STRING) (GooString*)
{
    $1 = PyString_AsString($input) ? 1 : 0;
}


%typemap(in) (Unicode *s, int len) 
{
  size_t len = PyUnicode_GET_SIZE($input);
    //printf("String memory size: %d", len);
    //fflush(stdout);
  if (PyUnicode_Check($input)) {
    size_t len = PyUnicode_GET_SIZE($input);
    if (len) {
         wchar_t * tmp = (wchar_t*) malloc(len*sizeof(char));
         $2 = PyUnicode_AsWideChar((PyUnicodeObject*)$input, tmp, len);
        $1 = (Unicode*)tmp;
     }
  }else{
    PyErr_SetString(PyExc_TypeError,"not a string type");
    return NULL; 
  }
}

//%typemap(freearg) Unicode* {
//  free($1);
//}

%typemap(in) (GooString*) 
{
  if (PyString_Check($input)) {
    $1 = new GooString(PyString_AsString($input),
        PyString_Size($input));
  }else{
    PyErr_SetString(PyExc_TypeError,"not a string type");
    return NULL; 
  }
}

//%typemap(freearg) GooString* {
//  delete($1);
//}

%typemap(out) (GooString*)
{
  $result = PyString_FromStringAndSize($1->getCString(), $1->getLength());
}

%inline
%{
extern GooString* test_goo_string(GooString* test, GooString* fifi=NULL)
{
  printf("%s \n", test->getCString());
  fflush(stdout);
  return test;
};
extern GooString* test_goo_string_new(GooString* test, GooString* fifi)
{
  printf("%s \n", test->getCString());
  fflush(stdout);
  return test;
};
%}


%include "poppler/poppler-config.h"
//should ignore inline method!
%ignore TextWord::primaryCmp(TextWord *word);

%include "poppler/splash/SplashBitmap.h"
%include "poppler/PDFDoc.h"
%include "poppler/OutputDev.h"
%include "poppler/Catalog.h"
%include "poppler/Page.h"
%include "poppler/SplashOutputDev.h"
%include "poppler/TextOutputDev.h"

%include "poppler/GlobalParams.h"
