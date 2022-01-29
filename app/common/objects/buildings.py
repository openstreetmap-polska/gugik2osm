import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .. import util
from .. import database as db


@dataclass
class ProposedBuilding:
    id: str
    building: str
    amenity: str
    man_made: str
    leisure: str
    historic: str
    tourism: str
    building_levels: int
    geometry: Dict[str, Any]

    @property
    def id_tags_geom_tuple(self) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """Returns tuple with object id, dict with tags and dict with geometry."""

        tags = {'source': 'www.geoportal.gov.pl'}
        if self.building:
            tags['building'] = self.building
        if self.amenity:
            tags['amenity'] = self.amenity
        if self.man_made:
            tags['man_made'] = self.man_made
        if self.leisure:
            tags['leisure'] = self.leisure
        if self.historic:
            tags['historic'] = self.historic
        if self.tourism:
            tags['tourism'] = self.tourism
        if self.building_levels:
            tags['building:levels'] = self.building_levels
        return self.id, tags, self.geometry


def nearest_building_geom_only(lon: float, lat: float, search_distance_in_meters: float) -> List[str]:
    """
    Returns the nearest building within search distance of given coordinates (geom only).
    Query automatically limits search distance to 0.005 degree regardless of parameters.
    It's a helper method to get some geometry to register data export.
    """

    data = db.data_from_db(
        query=db.QUERIES['josm_nearest_building_geom_only'],
        parameters={
            'lat': lat,
            'lon': lon,
            'search_distance': search_distance_in_meters,
        },
        row_as=tuple,
    )

    return [x[0] for x in data]


def nearest_building_josm_xml(lon: float, lat: float, search_distance_in_meters: float) -> list:
    """
    Returns the nearest building within search distance of given coordinates.
    Query automatically limits search distance to 0.005 degree regardless of parameters.
    """

    data = db.data_from_db(
        query=db.QUERIES['josm_nearest_building'],
        parameters={
            'lat': lat,
            'lon': lon,
            'search_distance': search_distance_in_meters,
        },
        row_as=dict,
    )

    return [util.input_feature_factory(**row) for row in data]


def proposed_buildings(bbox: Tuple[float, float, float, float]) -> List[ProposedBuilding]:
    """
    Returns proposed buildings within given bounding box. Returns list of instances of ProposedBuilding class.
    Proposed buildings are buildings that are present in gov database but are absent from OSM database.
    """

    data = db.data_from_db(db.QUERIES['sc_proposed_buildings_in_bbox'], bbox)
    return [ProposedBuilding(*a[:8], json.loads(a[8])) for a in data]


def proposed_buildings_geojson_dict(bbox: Tuple[float, float, float, float]) -> Dict[str, Any]:
    """
    Returns proposed buildings within given bounding box. Returns a dict with the structure of GeoJSON.
    Proposed buildings are buildings that are present in gov database but are absent from OSM database.
    """

    pb = proposed_buildings(bbox)
    data = [x.id_tags_geom_tuple for x in pb]
    features = [util.Feature(id=x[0], tags=x[1], geojson_geometry=x[2]) for x in data]
    return util.to_geojson_dict(features)


def report_buildings(ids: List[str]) -> None:
    """
    Adds building to a list of buildings marked as unsuitable for import. Or more precisely it adds it to a queue.
    After queue entry is processed this building will be removed from the map and won't be returned in future requests.
    """

    db.execute_batch(db.QUERIES['insert_to_exclude_bdot_buildings'], [(x,) for x in ids])


def report_buildings_in_polygon(geojson_geometry_string: str) -> None:
    """
    Adds building to a list of buildings marked as unsuitable for import. Or more precisely it adds it to a queue.
    After queue entry is processed this building will be removed from the map and won't be returned in future requests.
    """

    db.execute_query(
        db.QUERIES['insert_to_exclude_bdot_buildings_where_geom'],
        {'geojson_geometry': geojson_geometry_string}
    )
