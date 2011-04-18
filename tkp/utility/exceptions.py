"""

This module defines exceptions specific to the TKP package

"""


class TKPException(Exception):
    """General TKP exception"""

    pass


class TKPDataBaseError(TKPException):
    """Database exceptions specific to the TKP"""

    pass
