from __future__ import with_statement

"""

This recipe associate sources extracted from the current image
with those sources from previous images in the same dataset.
If you want to search through all previous sources, comment-out
the dataset_id in the parset

The parset requires the image_id; other parset parameters are the
association search radius in degrees (default of 90 arcsec), and the
source field density in sources/arcsec^2 (default 4.02e-6, which is
the NVSS source density).

Example parset:

dataset_id = 1             #
radius = 90                # association search radius of 90 arcsec
density = 4.02439375E-06   # source density; this is the NVSS source density

"""

__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010, University of Amsterdam'
__version__ = '0.1'
__last_modification__ = '2010-08-24'



import sys
import os

import numpy
import monetdb.sql.connections

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support import lofaringredient
from lofarpipe.cuisine.parset import Parset


SQL = {
    'init': """DELETE FROM tempbasesources""",
    'inserttemp': """\
INSERT INTO
  tempbasesources  
    (xtrsrc_id
    ,assoc_xtrsrc_id
    ,datapoints
    ,I_peak_sum
    ,I_peak_sq_sum
    ,weight_peak_sum
    ,weight_I_peak_sum
    ,weight_I_peak_sq_sum
    ,distance
    )
  SELECT
     b0.xtrsrc_id
    ,x0.xtrsrcid as assoc_xtrsrc_id
    ,b0.datapoints + 1 as datapoints  
    ,b0.I_peak_sum + x0.I_peak as i_peak_sum  
    ,b0.I_peak_sq_sum + x0.I_peak * x0.I_peak as i_peak_sq_sum  
    ,b0.weight_peak_sum + 1 /
      (x0.I_peak_err * x0.I_peak_err) as weight_peak_sum  
    ,b0.weight_I_peak_sum + x0.I_peak /
      (x0.I_peak_err * x0.I_peak_err) as weight_i_peak_sum  
    ,b0.weight_I_peak_sq_sum + x0.I_peak * x0.I_peak /
       (x0.I_peak_err * x0.I_peak_err) as weight_i_peak_sq_sum
    ,ASIN( SQRT((x0.x - b0.x)*(x0.x - b0.x) +
                (x0.y - b0.y)*(x0.y - b0.y) +
                (x0.z - b0.z)*(x0.z - b0.z) )/2 ) /
           SQRT(x0.ra_err * x0.ra_err +
                b0.ra_err * b0.ra_err +
                x0.decl_err * x0.decl_err +
                b0.decl_err * b0.decl_err)
        as distance    
  FROM
     basesources b0  
    ,extractedsources x0  
  WHERE x0.image_id = %s  
  AND b0.zone BETWEEN x0.zone - 1 AND x0.zone + 1  
  AND ASIN( SQRT( (x0.x - b0.x)*(x0.x - b0.x) +
                  (x0.y - b0.y)*(x0.y - b0.y) +
                  (x0.z - b0.z)*(x0.z - b0.z) )/2 ) /
            SQRT(x0.ra_err * x0.ra_err +
                 b0.ra_err * b0.ra_err +
                 x0.decl_err * x0.decl_err +
                 b0.decl_err * b0.decl_err)
      < %s
""",
    'deletemult': """\
DELETE FROM tempbasesources
WHERE tempsrcid in
(
    SELECT tb.tempsrcid FROM
    (
        SELECT xtrsrc_id, MIN(distance) AS mindistance
        FROM tempbasesources
        GROUP BY xtrsrc_id
        HAVING COUNT(*) > 1
    ) t
    ,tempbasesources tb
    WHERE
        tb.xtrsrc_id = t.xtrsrc_id
      AND
        tb.distance > t.mindistance
)
""",
    'updatetemp': """\
    UPDATE basesources
  SET
    datapoints = (
      SELECT datapoints
      FROM tempbasesources
      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id
      )
    ,i_peak_sum = (
      SELECT i_peak_sum
      FROM tempbasesources
      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id
      )
    ,i_peak_sq_sum = (
      SELECT i_peak_sq_sum
      FROM tempbasesources
      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id
      )
    ,weight_peak_sum = (
      SELECT weight_peak_sum
      FROM tempbasesources
      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id
      )
    ,weight_i_peak_sum = (
      SELECT weight_i_peak_sum
      FROM tempbasesources
      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id
      )
    ,weight_i_peak_sq_sum = (
      SELECT weight_i_peak_sq_sum
      FROM tempbasesources
      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id
      )
  WHERE EXISTS (
    SELECT xtrsrc_id
    FROM tempbasesources
    WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id
    )
    """,
    'insertbase': """\
INSERT INTO basesources 
  (xtrsrc_id 
   ,ds_id 
   ,image_id 
   ,zone 
   ,ra 
   ,decl 
   ,ra_err 
   ,decl_err 
   ,x 
   ,y 
   ,z 
   ,datapoints
   ,I_peak_sum 
   ,I_peak_sq_sum 
   ,weight_peak_sum 
   ,weight_I_peak_sum 
   ,weight_I_peak_sq_sum 
  ) 
  SELECT
     x1.xtrsrcid
    ,im1.ds_id 
    ,im1.imageid 
    ,x1.zone 
    ,x1.ra 
    ,x1.decl 
    ,x1.ra_err 
    ,x1.decl_err 
    ,x1.x 
    ,x1.y 
    ,x1.z 
    ,1 
    ,x1.I_peak 
    ,x1.I_peak * x1.I_peak 
    ,1 / (x1.I_peak_err * x1.I_peak_err) 
    ,x1.I_peak / (x1.I_peak_err * x1.I_peak_err) 
    ,x1.I_peak * x1.I_peak / (x1.I_peak_err * x1.I_peak_err) 
  FROM
     extractedsources x1 
    ,images im1 
   WHERE x1.image_id = %s 
     AND im1.imageid = x1.image_id 
     AND x1.xtrsrcid NOT IN
     (
       SELECT x0.xtrsrcid 
       FROM
          extractedsources x0 
         ,basesources b0 
       WHERE x0.image_id = %s 
       AND b0.zone BETWEEN x0.zone -1 AND x0.zone + 1 
       AND ASIN(SQRT((x0.x - b0.x)*(x0.x - b0.x) +
                     (x0.y - b0.y)*(x0.y - b0.y) +
                     (x0.z - b0.z)*(x0.z - b0.z) ) /2 ) /
                SQRT(x0.ra_err * x0.ra_err +
                     b0.ra_err * b0.ra_err +
                     x0.decl_err * x0.decl_err +
                     b0.decl_err * b0.decl_err)
                < %s
     )
    """,
    'assocfirst': """\
    INSERT INTO assocxtrsources
    (xtrsrc_id
    ,assoc_xtrsrc_id
    )
  SELECT
     x1.xtrsrcid as xtrsrc_id
    ,x1.xtrsrcid as assoc_xtrsrc_id
  FROM
     extractedsources x1 
    ,images im1 
   WHERE x1.image_id = %s 
     AND im1.imageid = x1.image_id 
     AND x1.xtrsrcid NOT IN (
       SELECT x0.xtrsrcid 
       FROM
          extractedsources x0 
         ,basesources b0 
       WHERE x0.image_id = %s 
       AND b0.zone BETWEEN x0.zone -1 AND x0.zone + 1 
       AND ASIN(SQRT((x0.x - b0.x)*(x0.x - b0.x) +
                     (x0.y - b0.y)*(x0.y - b0.y) +
                     (x0.z - b0.z)*(x0.z - b0.z) ) /2 ) /
                SQRT(x0.ra_err * x0.ra_err +
                     b0.ra_err * b0.ra_err +
                     x0.decl_err * x0.decl_err +
                     b0.decl_err * b0.decl_err)
           < %s
       )
    """,
    'assoc': """\
    INSERT INTO assocxtrsources
    ( xtrsrc_id
     ,assoc_xtrsrc_id
    )
    SELECT
     xtrsrc_id
    ,assoc_xtrsrc_id
    FROM tempbasesources
    """,
    'dataset': """\
SELECT ds_id FROM images WHERE imageid = %s
"""
    }


class DBConnectionField(lofaringredient.Field):
    def is_valid(self, value):
        return isinstance(value, monetdb.sql.connections.Connection)
    

class SourceAssociation(BaseRecipe):

    inputs = dict(
        parset=lofaringredient.StringField(
            '--parset', help="Source associaton parset"),
        dbconnection=DBConnectionField(
            '--dbconnection', help='')
        )    
    outputs = dict(
        image_id=lofaringredient.IntField(),
        dataset_id=lofaringredient.IntField(),
        )

    def go(self):
        super(SourceAssociation, self).go()
        self.logger.info("Associating sources from current image with "
                         "previous images in same dataset")
        params = Parset(os.path.join(
                self.config.get("layout", "parset_directory"),
                self.inputs['parset']))
        radius = params.getFloat('radius')/3600.
        density = params.getFloat('density')
        image_id = params.getInt('image_id')
        try:
            distance = params.getFloat('distance')*numpy.pi/3600/180
        except KeyError:
            distance = 7.2722e-06  # 1.5 arcsec
        self.outputs['image_id'] = image_id
        arguments = (density, image_id, radius, density, image_id, radius,
                     radius, density, image_id, radius, radius, density,
                     image_id, image_id, radius, image_id, radius)
        dbconn = self.inputs['dbconnection']
        cursor = dbconn.cursor()
        # find the dataset for this image
        cursor.execute(SQL['dataset'], (image_id,))
        self.outputs['dataset_id'] = int(cursor.fetchone()[0])
        cursor.execute(SQL['init'], ())
        dbconn.commit()
        cursor.execute(SQL['inserttemp'], (image_id, distance))
        dbconn.commit()
        cursor.execute(SQL['deletemult'], ())
        dbconn.commit()
        cursor.execute(SQL['updatetemp'], ())
        dbconn.commit()
        self.logger.info("%d sources associated" % cursor.rowcount)
        cursor.execute(SQL['insertbase'], (image_id, image_id, distance))
        dbconn.commit()
        cursor.execute(SQL['assocfirst'], (image_id, image_id, distance))
        dbconn.commit()
        cursor.execute(SQL['assoc'], ())
        dbconn.commit()
        return 0


if __name__ == '__main__':
    sys.exit(SourceAssociation().main())
