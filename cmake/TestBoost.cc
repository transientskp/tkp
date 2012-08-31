
#include <iostream>
#include <boost/version.hpp>

#ifdef TEST_BOOST_THREAD
/* Required header files*/
#include <boost/thread/thread.hpp>
#include <boost/thread/mutex.hpp>
/* Function to call */
void hello() {
  std::cout << "[TestBoost::hello] Hello world." << std::endl;
}
#endif 

int main ()
{

  /*________________________________________________________
    Library version
    BOOST_VERSION % 100 is the patch level
    BOOST_VERSION / 100 % 1000 is the minor version
    BOOST_VERSION / 100000 is the major version  
  */
  
  std::cout << "BOOST_VERSION "       << BOOST_VERSION          << std::endl;
  std::cout << "BOOST_VERSION_MAJOR " << BOOST_VERSION/100000   << std::endl;
  std::cout << "BOOST_VERSION_MINOR " << BOOST_VERSION/100%1000 << std::endl;
  std::cout << "BOOST_VERSION_PATCH " << BOOST_VERSION%100      << std::endl;
  std::cout << "BOOST_LIB_VERSION "   << BOOST_LIB_VERSION      << std::endl;
  
  /*________________________________________________________
    Test usage of thread library
  */
  
#ifdef TEST_BOOST_THREAD
  boost::thread _myThread (&hello);
  _myThread.join();
  _myThread.boost::thread::joinable();
#endif 
  
  return 1;
}
