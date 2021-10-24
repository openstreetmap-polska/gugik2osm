from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .. import database as db


@dataclass
class VectorTile:
    z: int
    x: int
    y: int
    data: bytes


def generate_if_not_exists(z: int, x: int, y: int) -> None:
    db.execute_query(db.QUERIES['mvt_insert'], {'z': z, 'x': x, 'y': y})


def select(z: int, x: int, y: int) -> Optional[VectorTile]:
    list_of_tiles = db.data_from_db(db.QUERIES['cached_mvt'], (z, x, y))
    if len(list_of_tiles) == 1:
        return VectorTile(z, x, y, list_of_tiles[0][0])
    else:
        return None


def queue_for_reload(z: int, x: int, y: int) -> None:
    db.execute_query(
        db.QUERIES['mvt_add_to_reload_queue'],
        (f'http_request_{datetime.now().isoformat()}', z, x, y)
    )
