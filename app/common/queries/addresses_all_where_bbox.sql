select
    GeometryType(d.geom_2180) geom_type,
    case
        when d.teryt_ulica is null or d.teryt_ulica = '' then
            jsonb_strip_nulls(jsonb_build_object(
               'addr:place', d.teryt_msc,
               'addr:city:simc', d.teryt_simc,
               'addr:housenumber', d.nr,
               'addr:postcode', d.pna,
               'source:addr', 'gugik.gov.pl'
            ))
        else
            jsonb_strip_nulls(jsonb_build_object(
               'addr:city', d.teryt_msc,
               'addr:city:simc', d.teryt_simc,
               'addr:street', d.teryt_ulica,
               'addr:housenumber', d.nr,
               'addr:postcode', d.pna,
               'source:addr', 'gugik.gov.pl'
            ))
   end tags,
   st_x(st_transform(d.geom_2180, 4326)) longitude,
   st_y(st_transform(d.geom_2180, 4326)) latitude
from addresses d
where d.geom_2180 && st_transform(ST_MakeEnvelope(%s, %s, %s, %s, 4326), 2180)
limit 50000
;
