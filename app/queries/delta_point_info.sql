select
   lokalnyid,
   teryt_msc,
   teryt_simc,
   teryt_ulica,
   teryt_ulic,
   nr,
   pna
from prg.delta
where lokalnyid = cast(%s as uuid);
