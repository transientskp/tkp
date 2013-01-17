UPDATE version 
   SET value = 9
 WHERE name = 'revision'
   AND value = 8
; %SPLIT%

ALTER TABLE image ADD COLUMN rejected BOOLEAN NOT NULL DEFAULT FALSE; %SPLIT%

UPDATE image 
   SET rejected = TRUE
 WHERE EXISTS (SELECT id
                FROM (SELECT i.id
                        FROM image i
                            ,rejection r
                       WHERE i.id = r.image
                     ) t
               WHERE t.id = image.id
              )
; %SPLIT%
