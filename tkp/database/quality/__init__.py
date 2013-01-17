from collections import namedtuple
import tkp.database


# todo: need to think of a way to sync this with tkp/database/tables/rejection.sql

RejectReason = namedtuple('RejectReason', 'id desc')

reason = {
    'rms': RejectReason(id=0, desc='RMS too high'),
    'beam': RejectReason(id=1, desc='beam invalid'),
    'bright_source': RejectReason(id=2, desc='bright source near'),
    }

query_reject = """\
INSERT INTO rejection 
  (image
  ,rejectreason
  ,comment
  )
VALUES 
  (%(imageid)s
  ,%(reason)s
  ,'%(comment)s'
  )
"""

query_update_image_rejected = """\
UPDATE image
   SET rejected = TRUE
 WHERE id = %(imageid)s
"""

query_unreject = """\
DELETE 
  FROM rejection 
 WHERE image=%(image)s
"""

query_isrejected = """\
SELECT rejectreason.description
      ,rejection.comment
  FROM rejection
      ,rejectreason
 WHERE rejection.rejectreason = rejectreason.id
   AND rejection.image = %(imageid)s
"""


def reject(connection, imageid, reason, comment):
    """ Add a reject intro to the database for a given image
    Args:
        connection: A database connection object
        image: The image ID of the image to reject
        reason: why is the image rejected, a defined in tkp.database.quality.reason
        comment: an optional comment with details about the reason
    """
    # Enter the entry in reject
    args = {'imageid': imageid, 'reason': reason, 'comment': comment}
    query = query_reject % args
    tkp.database.query(connection, query, commit=True)
    
    # Update the image record
    args = {'imageid': imageid}
    query = query_update_image_rejected % args
    tkp.database.query(connection, query, commit=True)


def unreject(connection, imageid):
    """ Remove all rejection of a given imageid
    Args:
        connection: A database connection object
        image: The image ID of the image to reject
    """
    query = query_unreject % {'image': imageid}
    tkp.database.query(connection, query, commit=True)


def isrejected(connection, imageid):
    """ Find out if an image is rejected or not
    Args:
        connection: A database connection object
        image: The image ID of the image to reject
    returns:
        False if not rejected, a list of reason id's if rejected
    """
    query = query_isrejected % {'imageid': imageid}
    cursor = tkp.database.query(connection, query)
    results = cursor.fetchall()
    if len(results) > 0:
        return ["%s: %s" % row for row in results]
    else:
        return False


