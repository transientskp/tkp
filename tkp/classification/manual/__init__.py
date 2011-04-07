"""

The Transient class, which represents a transient detected in the
pipeline, is defined in transient.py

Some other classes defined in utils.py are the Position and DateTime
class, which represent an astronomical position and a datetime-stamp,
both with an accuracy.

"""

from .classify import ClassificationSchema, ExternalTrigger, DataBase
from .utils import Position, DateTime
from .transient import Transient
