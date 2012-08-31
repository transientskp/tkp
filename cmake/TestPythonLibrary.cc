
#include <iostream>
#include <Python.h>
#include <modsupport.h>

int main ()
{
  
  /* Library version */

  std::cout << "PY_MAJOR_VERSION " << PY_MAJOR_VERSION << std::endl;
  std::cout << "PY_MINOR_VERSION " << PY_MINOR_VERSION << std::endl;
  std::cout << "PY_MICRO_VERSION " << PY_MICRO_VERSION << std::endl;

  /* Python API version */

  std::cout << "PYTHON_API_VERSION " << PYTHON_API_VERSION << std::endl;

  return 1;
}
