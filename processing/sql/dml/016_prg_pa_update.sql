update prg.pa
set osm_ulica = osm_street_name
from street_names_mappings
where teryt_simc_code=teryt_simc and teryt_ulic_code=teryt_ulic
;
