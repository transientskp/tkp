.. _documentation:


Documentation
=============

All functions should have a docstring with a short description of what the
function does. Also all arguments should be described in the docstring in the
following form::

  def function(var1, var2=False):
    """
    Description of the function.

    :param var1: description of var1
    :param var2: description of var2
    :type var2: bool (optional)
    :returns: bool
    :raises: Exception
    """
    if var2:
        raise Exception
    else:
        return True
