
import tkp.database

# todo: need to think of a way to sync this with tkp/database/tables/rejection.sql
reason = {
    'rms': 0,
    }

def reject(connection, image, reason, comment):
    q = "INSERT INTO rejection (image, rejectreason, comment) VALUES (%(image)s, %(reason)s, '%(comment)s')"
    args = {'image': image, 'reason': reason, 'comment': comment}
    query = q % args
    tkp.database.query(connection, query, commit=True)


def unreject(connection, image):
    query = "DELETE FROM rejection WHERE image=%(image)s" % {'image': image}
    tkp.database.query(connection, query, commit=True)
