
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
#include <stdio.h>
#include <wchar.h>

#include "Link.h"
%}
%include "typemaps.i"

typedef bool GBool;
typedef unsigned char SplashColor[4];

//for TextWord::getBBox()
%apply double *OUTPUT {double *xMinA, double *yMinA, double *xMaxA, double *yMaxA};
%apply double *OUTPUT {double *xMin, double *yMin, double *xMax, double *yMax};

/***************** SplashColorPtr *****************/

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

%typemap(typecheck) (SplashColorPtr)
{
 $1 = PyTuple_Check($input);
}
%{
  //globalParams = NULL;
  void init()
  {
    if (globalParams != NULL){
      delete(globalParams);
    }
    globalParams = new GlobalParams();
  }
%}
void init();

%typemap(in) SplashColorPtr { 
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
    // TODO: To be changed: values are static
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

%typemap(newfree) GooString* {
  if ($1 != NULL)
  {
    delete($1);
    $1 = NULL;
    }
}

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

/************** Unicode *******************/


%typemap(in) (Unicode *s, int len) 
{
  size_t len = PyUnicode_GET_SIZE($input);
    //printf("String memory size: %d", len);
    //fflush(stdout);
  if (PyUnicode_Check($input)) {
    size_t len = PyUnicode_GET_SIZE($input);
    if (len > 0) {
        //check if it is work with all version of python
         wchar_t * tmp = (wchar_t*) malloc(PyUnicode_GET_DATA_SIZE($input)); // malloc(len*sizeof(char));
         $2 = PyUnicode_AsWideChar((PyUnicodeObject*)$input, tmp, len) ;
         $1 = (Unicode*)tmp;
     }
  }else{
    PyErr_SetString(PyExc_TypeError,"not a string type");
    return NULL; 
  }
}


%typemap(freearg) (Unicode *s, int len)
{
  if ($1 != NULL)
  {
    free($1);
    $1 = NULL;
  }
  //delete($1);
}

%inline %{
GBool newOutlineLevel(Object *node, Catalog* catalog, PyObject* dic, int level=1)
{
  Object curr, next;
  GBool atLeastOne = gFalse;
  int page_number = -1;
  GooString * label = NULL;
  PyObject* childs = PyList_New(0);
  PyObject * local_dic =  PyDict_New();
  PyDict_SetItemString(local_dic, "childs", childs);

  if (node->dictLookup("First", &curr)->isDict()) {
    do {
      // get title, give up if not found
      Object title;
      if (curr.dictLookup("Title", &title)->isNull()) {
        title.free();
        break;
      }

      label = new GooString(title.getString());

      // get corresponding link
      GooString *linkName = NULL;;
      Object dest;
      curr.dictLookup("A", &dest);

      if (!dest.isNull())
      {
        LinkGoTo* action = (LinkGoTo *)LinkAction::parseAction(&dest);
        LinkDest* link_dest = catalog->findDest(action->getNamedDest());
        int page_number = 0;

        if (link_dest){
          if (link_dest->isPageRef()){
            Ref pageref = link_dest->getPageRef();
            page_number = catalog->findPage(pageref.num, pageref.gen);
          }
          else {
            page_number = link_dest->getPageNum();
          }
          printf("%d\n", page_number);
        }
        delete(link_dest);
        delete(action);
      }

      if (!curr.dictLookup("Dest", &dest)->isNull())
      {
        //printf("Dest not Null");
        LinkGoTo *link = new LinkGoTo(&dest);
        LinkDest *linkdest=NULL;
        if (link->getDest()!=NULL)
          linkdest=link->getDest()->copy();
        else if (link->getNamedDest()!=NULL)
          linkdest=catalog->findDest(link->getNamedDest());

        delete link;
        if (linkdest) {
          int page;
          if (linkdest->isPageRef()) {
            Ref pageref=linkdest->getPageRef();
            page=catalog->findPage(pageref.num,pageref.gen);
          } else {
            page=linkdest->getPageNum();
          }
          printf("%d\n", page);
          delete linkdest;
        }
      }
      dest.free();

      if (linkName)
        printf("%s", linkName->getCString());

      newOutlineLevel( &curr, catalog, local_dic, level+1);
      curr.dictLookup("Next", &next);
      curr.free();
      curr = next;
    } while(curr.isDict());
  }
  curr.free();
  if (label != NULL){
         PyDict_SetItemString(local_dic, "label", PyString_FromStringAndSize(label->getCString(), label->getLength()));
         PyDict_SetItemString(local_dic, "page_number", PyInt_FromLong(page_number));
        //label.free();
}
        PyObject* to_append = PyDict_GetItemString(dic, "childs");
        PyList_Append(to_append, local_dic);
  return atLeastOne;
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
%include "poppler/GlobalParams.h"

%extend PDFDoc {
  PyObject* getToc(){ 
        printf("Test\n");
       PyObject * dic =  PyDict_New();
  PyObject* childs = PyList_New(0);
  PyDict_SetItemString(dic, "childs", childs);
        newOutlineLevel(self->getCatalog()->getOutline(), self->getCatalog(), dic);
        return dic;
  };
};

%newobject TextPage::makeWordList;
%newobject TextOutputDev::takeText;
%newobject TextWord::getText;
%include "poppler/TextOutputDev.h"
%extend TextPage {
  ~TextPage(){ 
    self->decRefCnt(); 
  };
};
