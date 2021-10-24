from dataclasses import dataclass
from random import random, choice

from common import database as db


@dataclass
class Location:
    longitude: float
    latitude: float


def random_location() -> Location:
    """Returns random location (lon, lat) while prioritizing (95% chance) areas with a lot of objects to export."""

    if random() > 0.05:
        query = db.QUERIES['locations_most_count']
    else:
        query = db.QUERIES['locations_random']
    list_of_tuples = db.data_from_db(query, row_as=Location)

    return choice(list_of_tuples)
