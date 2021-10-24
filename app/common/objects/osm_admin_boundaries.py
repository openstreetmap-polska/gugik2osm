from dataclasses import dataclass
from typing import List

from common import database as db


@dataclass
class GeoJSONGeometryString:
    value: str


def select_where_terc(terc_code: str) -> List[GeoJSONGeometryString]:
    """Returns GeoJSON string with geometry of administrative boundary in OSM with given TERYT terc code."""

    return db.data_from_db(db.QUERIES['admin_geom_where_terc'], {'terc_code': terc_code}, GeoJSONGeometryString)


def select_where_simc(simc_code: str) -> List[GeoJSONGeometryString]:
    """Returns GeoJSON string with geometry of administrative boundary in OSM with given TERYT simc code."""

    return db.data_from_db(db.QUERIES['admin_geom_where_simc'], {'simc_code': simc_code}, GeoJSONGeometryString)


def select_where_id(relation_id: int) -> List[GeoJSONGeometryString]:
    """Returns GeoJSON string with geometry of administrative boundary in OSM with given OSM relation id."""

    return db.data_from_db(db.QUERIES['admin_geom_where_id'], {'relation_id': relation_id}, GeoJSONGeometryString)
