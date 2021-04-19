import mercantile as m
import csv

with open('~/tiles_6_14.tsv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for i, t in enumerate(m.tiles(14.0, 49.0, 24.03, 54.86, [6, 7, 8, 9, 10, 11, 12, 13, 14])):
        b = m.xy_bounds(t)
        geom = f'POLYGON (({b.left} {b.bottom}, {b.left} {b.top}, {b.right} {b.top}, {b.right} {b.bottom}, {b.left} {b.bottom}))'
        writer.writerow((t.z, t.x, t.y, geom))

# load to postgresql using
# source /opt/gugik2osm/conf/.env
# cat tiles_6_14.tsv | psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "copy temp_tiles_bounds FROM stdin with CSV delimiter '|'"
