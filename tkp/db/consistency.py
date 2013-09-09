import logging
import tkp.db

logger = logging.getLogger(__name__)

# The three queries below were know to give a count > 0
# when the db got into an inconsistent state.
# Therefore, before every run we do a check on these numbers
query_id0 = """\
SELECT COUNT(*)
  FROM extractedsource
 WHERE id = 0
"""

query_image0 = """\
SELECT COUNT(*)
  FROM extractedsource
 WHERE image = 0
"""

query_zone0 = """\
SELECT COUNT(*)
  FROM extractedsource
 WHERE id = 0
   AND image = 0
   AND zone = 0
"""


def check():
    """ Checks for any inconsistent values in tables
    """
    isconsistent(query_id0)
    isconsistent(query_image0)
    isconsistent(query_zone0)

def isconsistent(query):
    """ Counting rows should return 0, otherwise database is 
    in inconsistent state
    """
    cursor = tkp.db.execute(query, commit=True)
    results = zip(*cursor.fetchall())
    
    consistent = False
    if len(results) != 0:
        count = results[0][0]
        if count == 0:
            consistent = True
        else:
            raise ValueError("Inconsistent database\n %s returns %s" % (query, count))
    else:
        raise ValueError("No consistency check possible for database")
    
    return consistent

