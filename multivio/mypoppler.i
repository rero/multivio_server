
%module mypoppler
%{
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
%}
%include "typemaps.i"

//%include "poppler/goo/gtypes.h"
//%include "poppler/splash/SplashTypes.h"
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
  $result = PyString_FromStringAndSize((char*) $1, 3*arg1->getWidth()*arg1->getHeight());
}


class GooString {
public:
  // Create a string from a C string.
  GooString(const char *sA);
};

%include "poppler/splash/SplashBitmap.h"
%include "poppler/PDFDoc.h"
%include "poppler/OutputDev.h"
%include "poppler/Catalog.h"
%include "poppler/Page.h"
%include "poppler/SplashOutputDev.h"
%include "poppler/GlobalParams.h"
