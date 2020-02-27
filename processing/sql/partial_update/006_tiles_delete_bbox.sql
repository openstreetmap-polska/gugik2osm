delete from tiles
where
  -- make sure given bounding box is valid
  ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)
  and
  tiles.bbox && ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)
  and
  z >= 13
;