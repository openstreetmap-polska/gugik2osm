update prg.pa
set osm_ulica = osm_name
from street_names_mappings
where teryt_ulica = original_name
;
