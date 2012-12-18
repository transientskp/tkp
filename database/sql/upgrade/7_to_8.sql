UPDATE version 
   SET value = 8
 WHERE name = 'revision'
   AND value = 7
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

