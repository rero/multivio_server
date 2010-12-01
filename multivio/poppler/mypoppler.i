
%module mypoppler
%{
#include "poppler-config.h"
#include "PDFDoc.h"
#include "goo/GooString.h"
#include "goo/gtypes.h"
#include "SplashOutputDev.h"
#include "GlobalParams.h"
#include "Catalog.h"
#include "Outline.h"
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
#include "PDFDocEncoding.h"

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
GBool newOutlineLevel(Object *node, Catalog* catalog, PyObject* list, int level=1)
{
  Object curr, next;
  GBool atLeastOne = gFalse;
  int page_number = -1;
  Unicode *title = NULL;
  int titleLen = 0;
  GooString* s = NULL;
  int i;

  if (node->dictLookup("First", &curr)->isDict()) {
    do {
      page_number = -1;
      // get title, give up if not found
      Object obj_title;
      if (curr.dictLookup("Title", &obj_title)->isString() && !(obj_title.isNull())) {
        s = obj_title.getString();
        if ((s->getChar(0) & 0xff) == 0xfe &&
            (s->getChar(1) & 0xff) == 0xff) {
          titleLen = (s->getLength() - 2) / 2;
          title = (Unicode *)gmallocn(titleLen, sizeof(Unicode));
          for (i = 0; i < titleLen; ++i) {
            title[i] = ((s->getChar(2 + 2*i) & 0xff) << 8) |
              (s->getChar(3 + 2*i) & 0xff);
          }
        } else {
          titleLen = s->getLength();
          title = (Unicode *)gmallocn(titleLen, sizeof(Unicode));
          for (i = 0; i < titleLen; ++i) {
            title[i] = pdfDocEncoding[s->getChar(i) & 0xff];
          }
        }
      } else {
        titleLen = 0;
        obj_title.free();
        break;
      }
      obj_title.free();
      if (titleLen == 0)
      {
          title = (Unicode *)gmallocn(1, sizeof(Unicode));
          titleLen = 1;
          title[0] = '\0';
      }

      // get corresponding link
      GooString *linkName = NULL;;
      Object dest;
      curr.dictLookup("A", &dest);
      if (!dest.isNull())
      {
        LinkGoTo* action = (LinkGoTo *)LinkAction::parseAction(&dest);
        if(action && action->isOk())
        {
          LinkDest *linkdest=NULL;
          if (action->getDest()!=NULL)
            linkdest=action->getDest()->copy();
          else if (action->getNamedDest()!=NULL)
            linkdest=catalog->findDest(action->getNamedDest());
          delete(action);

          if (linkdest)
          {
            if (linkdest->isPageRef())
            {
              Ref pageref = linkdest->getPageRef();
              page_number = catalog->findPage(pageref.num, pageref.gen);
            }
            else 
            {
              page_number = linkdest->getPageNum();
            }
            delete(linkdest);
          }
        }
        dest.free();
      }

      if (!curr.dictLookup("Dest", &dest)->isNull())
      {
        LinkGoTo *link = new LinkGoTo(&dest);
        LinkDest *linkdest=NULL;
        if (link->getDest()!=NULL)
          linkdest=link->getDest()->copy();
        else if (link->getNamedDest()!=NULL)
          linkdest=catalog->findDest(link->getNamedDest());
        delete link;

        if (linkdest) {
          if (linkdest->isPageRef()) {
            Ref pageref=linkdest->getPageRef();
            page_number=catalog->findPage(pageref.num,pageref.gen);
          } else {
            page_number=linkdest->getPageNum();
          }
          delete linkdest;
        }
        dest.free();
      }

      PyObject * local_dic =  PyDict_New();
      PyObject* childs = PyList_New(0);

      newOutlineLevel( &curr, catalog, childs, level+1);
      PyDict_SetItemString(local_dic, "label", PyUnicode_FromWideChar((const wchar_t *)title, titleLen));
      if(page_number < 1 or page_number >  catalog->getNumPages()) 
        PyDict_SetItemString(local_dic, "page_number", Py_None);
      else
        PyDict_SetItemString(local_dic, "page_number", PyInt_FromLong(page_number));
      if (PyList_Size(childs) > 0)
        PyDict_SetItemString(local_dic, "childs", childs);
      PyList_Append(list, local_dic);

      curr.dictLookup("Next", &next);
      curr.free();
      gfree(title);
      curr = next;
    } while(curr.isDict());
  }
  curr.free();
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
        //printf("Test\n");
        PyObject* childs = PyList_New(0);
        Object* outline = self->getCatalog()->getOutline();
        if (outline != NULL && outline->isDict())
        {
          newOutlineLevel(outline, self->getCatalog(), childs);
        }
        return childs;
  };
  PyObject* getInfo()
  {
    Object info;
    Object obj;
    PyObject * dic =  PyDict_New();
    Unicode *title = NULL;
    int titleLen = 0;
    GooString* s = NULL;
    if (!self->getDocInfo(&info)->isDict()) {
      info.free();
      return dic;
    } 

    Dict *info_dict = info.getDict();
    for (int i = 0; i < info_dict->getLength(); ++i) {
      char* key = info_dict->getKey(i);
      if (info_dict->lookup(key, &obj)->isString()) {
        s = obj.getString();
        if ((s->getChar(0) & 0xff) == 0xfe &&
            (s->getChar(1) & 0xff) == 0xff) {
          titleLen = (s->getLength() - 2) / 2;
          title = (Unicode *)gmallocn(titleLen, sizeof(Unicode));
          for (int j = 0; j < titleLen; ++j) {
            title[j] = ((s->getChar(2 + 2*j) & 0xff) << 8) |
              (s->getChar(3 + 2*j) & 0xff);
          }
        } else {
          titleLen = s->getLength();
          title = (Unicode *)gmallocn(titleLen, sizeof(Unicode));
          for (int j = 0; j < titleLen; ++j) {
            title[j] = pdfDocEncoding[s->getChar(j) & 0xff];
          }
        }
        if (titleLen == 0)
        {
          title = (Unicode *)gmallocn(1, sizeof(Unicode));
          titleLen = 1;
          title[0] = '\0';
        }
        if(titleLen > 0)
          PyDict_SetItemString(dic, key, PyUnicode_FromWideChar((const wchar_t *)title, titleLen));
       gfree(title);
      }
      obj.free();
    }  //end of for
    info.free();
    return dic;
  };
};

%newobject TextPage::makeWordList;
%newobject TextOutputDev::takeText;
%newobject TextWord::getText;
%newobject TextPage::getText;
%include "poppler/TextOutputDev.h"
%extend TextPage {
  ~TextPage(){ 
    self->decRefCnt(); 
  };
};

