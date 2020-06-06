import mercantile as m

with open('./cache_low_zoom_tiles.sh', 'w', encoding='UTF-8') as f:
    for tile in m.tiles(14.0, 49.0, 24.03, 54.86, [6, 7, 8, 9, 10, 11, 12]):
        f.write(f'curl -s localhost/tiles/{tile.z}/{tile.x}/{tile.y}.pbf > /dev/null \n')
