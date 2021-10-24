import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .. import util
from .. import database as db


@dataclass
class ProposedAddress:
    id: str
    city: str
    teryt_simc: str
    street: str
    house_number: str
    post_code: str
    geometry: Dict[str, Any]

    @property
    def id_tags_geom_tuple(self) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """Returns tuple with object id, dict with tags and dict with geometry."""

        tags = {'addr:housenumber': self.house_number, 'source:addr': 'gugik.gov.pl'}
        if self.post_code:
            tags['addr:postcode'] = self.post_code
        if self.teryt_simc:
            tags['addr:city:simc'] = self.teryt_simc
        if self.street:
            tags['addr:street'] = self.street
            tags['addr:city'] = self.city
        else:
            tags['addr:place'] = self.city
        return self.id, tags, self.geometry


def proposed_addresses(bbox: Tuple[float, float, float, float]) -> List[ProposedAddress]:
    """
    Returns proposed addresses within given bounding box. Returns list of instances of ProposedAddress class.
    Proposed addresses are addresses that are present in gov database but are absent from OSM database.
    """

    data = db.data_from_db(db.QUERIES['sc_proposed_addresses_in_bbox'], bbox)
    return [ProposedAddress(*a[:6], json.loads(a[6])) for a in data]


def proposed_addresses_geojson_dict(bbox: Tuple[float, float, float, float]) -> Dict[str, Any]:
    """
    Returns proposed addresses within given bounding box. Returns a dict with the structure of GeoJSON.
    Proposed addresses are addresses that are present in gov database but are absent from OSM database.
    """

    pa = proposed_addresses(bbox)
    data = [x.id_tags_geom_tuple for x in pa]
    features = [util.Feature(id=x[0], tags=x[1], geojson_geometry=x[2]) for x in data]
    return util.to_geojson_dict(features)


def report_addresses(ids: List[str]) -> None:
    """
    Adds address to a list of addresses marked as unsuitable for import. Or more precisely it adds it to a queue.
    After queue entry is processed this address will be removed from the map and won't be returned in future requests.
    """

    db.execute_batch(db.QUERIES['insert_to_exclude_prg'], [(x,) for x in ids])


def report_addresses_in_polygon(geojson_geometry_string: str) -> None:
    """
    Adds address to a list of addresses marked as unsuitable for import. Or more precisely it adds it to a queue.
    After queue entry is processed this address will be removed from the map and won't be returned in future requests.
    """

    db.execute_query(
        db.QUERIES['insert_to_exclude_prg_addresses_where_geom'],
        {'geojson_geometry': geojson_geometry_string}
    )
