// A simple wrapper to call wcslib from Python.
// Originally by Alexander Usov.
// Taken from USG SVN revision 1206.

// Compile using cmake:
//   $ cmake .
//   $ make
//   # make install
// (The naive CMakeLists.txt currently assumes Python 2.4 and that you have
// wcslib installed under /usr/local/(include|lib).

// This code implements a Python interface to the 'middle layer' of wcslib.
// That is, it does not attempt to parse FITS files itself (the 'top layer')
// and does not directly address the low-level mathematical routines.
// 
// Brief usage example:
//
// import wcslib
// wcs = wcslib.wcs()
// wcs.crval = (CRVAL1, CRVAL2) # All params from e.g. FITS header
// wcs.crpix = (CRPIX1, CRPIX2) # NB: not limited to two axes.
// wcs.cdelt = (CDELT1, CDELT2)
// wcs.crota = (CROTA1, CROTA2)
// wcs.ctype = (CTYPE1, CTYPE2) # 'RA---SIN', 'DEC--SIN' for e.g.
// wcs.cunit = (CUNIT1, CUNIT2) # 'deg', 'deg' for e.g.
// # could call wcs.wcsset() here, but it's not actually necessary
// wcs.pprint()                 # print settings
// wcs.p2s([pixel_x, pixel_y])  # pixel to spatial
// wcs.s2p([ra, dec])           # spatial to pixel

#include <vector>
#include <boost/python.hpp>
#include <boost/python/detail/api_placeholder.hpp>
#include <wcs.h>

using namespace boost::python;
using namespace std;

struct wcs
{
  wcsprm *_wcs;
  bool _init;

  wcs(int naxis = 2) {
    wcsprm *w = (wcsprm*)calloc(1, sizeof(wcsprm));
    w->flag = -1; // Only for the first wcsini
    wcsini(1, naxis, w);

    _wcs = w;
    _init = false;
  }

  ~wcs() {
    wcsfree(_wcs);
    free(_wcs);
  }

  void wcsset() {
    int err = ::wcsset(_wcs);

    if (err) {
      PyErr_Format(PyExc_RuntimeError, "wcsset error: %d: %s",
		   err, wcs_errmsg[err]);
      throw error_already_set();
    }
  }

  void print() {
    wcsprt(_wcs);
  }

  // set array of double's in wcsprm
  template<double* wcsprm::* P>
  void set_field_double(object arg)
  {
    if (len(arg) != _wcs->naxis) {
      PyErr_SetString(PyExc_TypeError, "list of NAXIS values expected");
      throw error_already_set();
    }

    for (int i = 0; i < len(arg); ++i)
      (_wcs->*P)[i] = extract<double>(arg[i]);
  }

  // read array of double's in wcsprm
  template<double* wcsprm::* P>
  object get_field_double()
  {
    list res;

    for (int i = 0; i < _wcs->naxis; ++i)
      res.append((_wcs->*P)[i]);
    
    return tuple(res);
  }

  // set array of strings's in wcsprm
  template<char (* wcsprm::*P)[72]>
  void set_field_string(object arg)
  {
    if (len(arg) != _wcs->naxis) {
      PyErr_SetString(PyExc_TypeError, "list of NAXIS values expected");
      throw error_already_set();
    }

    for (int i = 0; i < len(arg); ++i)
      strncpy((_wcs->*P)[i], extract<char *>(arg[i]), 72);
  }

  // get array of strings's in wcsprm
  template<char (* wcsprm::*P)[72]>
  object get_field_string()
  {
    list res;

    for (int i = 0; i < _wcs->naxis; ++i)
      res.append((_wcs->*P)[i]);
    
    return tuple(res);
  }

  object p2s(object arg)
  {
    if (len(arg) % _wcs->naxis != 0) {
      PyErr_SetString(PyExc_TypeError, "list of X*NAXIS values expected");
      throw error_already_set();
    }

    int ntotal = len(arg);
    int ncoord = ntotal / _wcs->naxis;
    int err;
    vector<double> pixcrd(ntotal), imgcrd(ntotal), world(ntotal),
      phi(ncoord), theta(ncoord);
    vector<int> stat(ncoord);

    for(int i = 0; i < ntotal; ++i)
      pixcrd[i] = extract<double>(arg[i]);

    err = wcsp2s(_wcs, ncoord, _wcs->naxis, &pixcrd[0], &imgcrd[0],
		 &phi[0], &theta[0], &world[0], &stat[0]);

    if (err)
      {
	PyErr_Format(PyExc_RuntimeError, "wcsp2s error: %d: %s",
		     err, wcs_errmsg[err]);
	throw error_already_set();
      }

    list res;
    for(int i = 0; i < ntotal; ++i)
      res.append(world[i]);

    return res;
  }

  object s2p(object arg)
  {
    if (len(arg) % _wcs->naxis != 0) {
      PyErr_SetString(PyExc_TypeError, "list of X*NAXIS values expected");
      throw error_already_set();
    }

    int ntotal = len(arg);
    int ncoord = ntotal / _wcs->naxis;
    int err;
    vector<double> pixcrd(ntotal), imgcrd(ntotal), world(ntotal),
      phi(ncoord), theta(ncoord);
    vector<int> stat(ncoord);

    for(int i = 0; i < ntotal; ++i)
      world[i] = extract<double>(arg[i]);

    err = wcss2p(_wcs, ncoord, _wcs->naxis, &world[0], &phi[0], &theta[0],
		 &imgcrd[0], &pixcrd[0], &stat[0]);

    if (err)
      {
	PyErr_Format(PyExc_RuntimeError, "wcsp2s error: %d: %s",
		     err, wcs_errmsg[err]);
	throw error_already_set();
      }

    list res;
    for(int i = 0; i < ntotal; ++i)
      res.append(pixcrd[i]);

    return res;
  }

private:
  // prevent copying
  wcs(const wcs&) {}
};


BOOST_PYTHON_MODULE(wcslib)
{
  class_<wcs, boost::noncopyable>("wcs")
    .def("wcsset", &wcs::wcsset)
    .def("pprint", &wcs::print)
    .def("p2s", &wcs::p2s)
    .def("s2p", &wcs::s2p)
    .add_property("crval", &wcs::get_field_double<&wcsprm::crval>,
		  &wcs::set_field_double<&wcsprm::crval>)
    .add_property("crpix", &wcs::get_field_double<&wcsprm::crpix>,
		  &wcs::set_field_double<&wcsprm::crpix>)
    .add_property("cdelt", &wcs::get_field_double<&wcsprm::cdelt>,
		  &wcs::set_field_double<&wcsprm::cdelt>)
    .add_property("crota", &wcs::get_field_double<&wcsprm::crota>,
		  &wcs::set_field_double<&wcsprm::crota>)
    .add_property("ctype", &wcs::get_field_string<&wcsprm::ctype>,
		  &wcs::set_field_string<&wcsprm::ctype>)
    .add_property("cunit", &wcs::get_field_string<&wcsprm::cunit>,
		  &wcs::set_field_string<&wcsprm::cunit>)


    ;
		  
}
