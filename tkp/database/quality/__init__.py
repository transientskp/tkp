
import tkp.database

# todo: need to think of a way to sync this with tkp/database/tables/rejection.sql
reason = {
    'rms': 0,
    }

def reject(connection, imageid, reason, comment):
    """ Add a reject intro to the database for a given image
    Args:
        connection: A database connection object
        image: The image ID of the image to reject
        reason: why is the image rejected, a defined in tkp.database.quality.reason
        comment: an optional comment with details about the reason
    """
    q = "INSERT INTO rejection (image, rejectreason, comment) VALUES (%(imageid)s, %(reason)s, '%(comment)s')"
    args = {'imageid': imageid, 'reason': reason, 'comment': comment}
    query = q % args
    tkp.database.query(connection, query, commit=True)


def unreject(connection, imageid):
    """ Remove all rejection of a given imageid
    Args:
        connection: A database connection object
        image: The image ID of the image to reject
    """
    query = "DELETE FROM rejection WHERE image=%(image)s" % {'image': imageid}
    tkp.database.query(connection, query, commit=True)

def isrejected(connection, imageid):
    """ Find out if an image is rejected or not
    Args:
        connection: A database connection object
        image: The image ID of the image to reject
    returns:
        False if not rejected, reason id if rejected
    """
    query = "SELECT rejectreason FROM rejection WHERE image=%(image)s" % {'image': imageid}
    cursor = tkp.database.query(connection, query, commit=True)
    rejections = cursor.fetchall()
    if len(rejections) > 0:
        return rejections[0][0]
