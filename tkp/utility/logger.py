import os, sys
import logging


def add_logger(func):
    """
    Decorator that provides a function with an extra logger argument
    and variable
    
    This decorator adds an extra keyword argument to a function,
    'logger'. By default this is None, but a logging.Logger can be
    provided.  If None, a default logger.Logger will be created for
    the function.
    
    This also adds a temporary logger variable to the global
    namespace, for the duration of the function. Thus, one can apply
    this decorator to a function, and then call logger.warn() or
    variants inside that function.
    
    Using the extra keyword argument, one can supply a formatted
    logger to the function, instead of relying on a default
    format. This is mostly convenient in the context of running a
    pipeline, because the logging outputs inside tkp functions will
    adhere to the format of the pipeline logger.
    
    The basic code was taken from
    http://stackoverflow.com/questions/591200/can-i-use-a-decorator-to-mutate-the-local-scope-of-a-function-in-python

    **Note**: The overall reply to the question asked above is "don't do it".
    Thus, using this decorator may actually be a bad idea, since it introduces a
    variable into the (global) namespace out of nowhere.
    Feel free to remove this decorator if deemed dangerous or otherwise unwise.

    To do:
    At some point, it will be better to remove the logging decorator to functions
    by moving the functions inside a class.
    Is it possible to easily set the global RootLogger (logging.warn() etc) to the
    pipeline logger? Otherwise, perhaps use a global TKP logger.
    
    Example:
    
        >>> from logger import add_logger
        >>> @add_logger
        ... def mult(a, b):
        ...   logger.info("Multiplying %f and %f" % (a, b))
        ...   return a*b
        ...
        >>> # use with default logger; no output, since default level = logging.WARNING
        >>> mult(3, 4)
        12
        >>> import logging
        >>> logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",level=logging.DEBUG)
        >>> logger = logging.getLogger()
        >>> # use with user defined logger
        >>> mult(5, 6, logger=logger)
        2011-02-07 14:58:05,955 - INFO - Multiplying 5.000000 and 6.000000
        30
    
    """

    def logged_func(*args, **kwargs):
        logger = kwargs.pop('logger', None)
        if logger is None:  # set up a default logger
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            handler.setLevel(logging.WARNING)
            logger = logging.getLogger("Base logger")
            logger.addHandler(handler)
            logger.setLevel(logging.WARNING)
        # Add/replace the global logger
        if 'logger' in func.func_globals:
            global_logger = (func.func_globals['logger'],)  # tuple is immutable
        else:
            global_logger = None
        try:
            func.func_globals['logger'] = logger
            result = func(*args, **kwargs)
        finally:
            if global_logger is None:
                del(func.func_globals['logger'])
            else:
                func.func_globals['logger'] = global_logger[0]
        return result
    return logged_func
