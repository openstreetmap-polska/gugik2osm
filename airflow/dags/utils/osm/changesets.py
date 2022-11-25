import gzip
import logging
import urllib.parse
import xml.dom.pulldom
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Dict, Generator, Union, Iterable
from xml.dom.minidom import Element

from .. import send_request, parse_bool
from .replication import (
    ReplicationSequence,
    format_replication_sequence,
    REPLICATION_CHANGESETS_URL,
    replication_sequence_to_int,
)


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Changeset:
    id: int
    created_at: datetime
    closed_at: datetime
    open: bool
    num_changes: int
    user: str
    uid: int
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    comments_count: int
    tags: Dict[str, str]

    def transform_to_dict(self):
        data = self.__dict__
        data["created_by"] = self.tags.get("created_by")
        data["source"] = self.tags.get("source")
        data["locale"] = self.tags.get("locale")
        data["bot"] = self.tags.get("bot")
        data["review_requested"] = self.tags.get("review_requested")
        data["hashtags"] = self.tags.get("hashtags")
        return data


def get_changeset_replication_sequence(url: str) -> ReplicationSequence:
    """Helper method that download state yaml file from given url and parses our sequence number and timestamp."""

    response = send_request(url)
    data = response.text.splitlines()
    ts = data[1].split("=")[1]
    ts_components = ts.split(" ")
    ts_fixed = f"{ts_components[0]} {ts_components[1][:-3]}{ts_components[2]}"
    seq = data[2].split("=")[1]
    dt = datetime.fromisoformat(ts_fixed)

    return ReplicationSequence(timestamp=dt, number=int(seq), formatted=format_replication_sequence(seq))


def find_newest_changeset_replication_sequence(
    replication_url: str = REPLICATION_CHANGESETS_URL
) -> ReplicationSequence:
    """Checks what's the newest changeset sequence number in OSM replication log."""
    url = urllib.parse.urljoin(replication_url, "state.yaml")
    return get_changeset_replication_sequence(url)


def download_and_parse_changeset_file(url: str) -> Generator[Changeset, None, None]:
    """Downloads gzip compressed XML file from URL and parses out Changeset."""

    response = send_request(url)
    LOGGER.info("Decompressing...")
    xml_data = gzip.GzipFile(fileobj=BytesIO(response.content))
    LOGGER.info("Parsing XML...")
    event_stream = xml.dom.pulldom.parse(xml_data)
    counter = 0
    for event, element in event_stream:
        element: Element = element  # just for typing
        if event == xml.dom.pulldom.START_ELEMENT and element.tagName == "changeset":
            event_stream.expandNode(element)
            tags = {}
            for child in element.childNodes:
                child: Element = child  # for typing
                counter += 1
                if type(child) == Element and child.tagName == "tag":
                    tags[child.getAttribute("k")] = child.getAttribute("v")
            yield Changeset(
                id=int(element.getAttribute("id")),
                created_at=datetime.fromisoformat(element.getAttribute("created_at")),
                closed_at=datetime.fromisoformat(element.getAttribute("closed_at")),
                open=parse_bool(element.getAttribute("open")),
                num_changes=int(element.getAttribute("num_changes")),
                user=element.getAttribute("user"),
                uid=int(element.getAttribute("uid")),
                min_lat=float(element.getAttribute("min_lat")),
                max_lat=float(element.getAttribute("max_lat")),
                min_lon=float(element.getAttribute("min_lon")),
                max_lon=float(element.getAttribute("max_lon")),
                comments_count=int(element.getAttribute("comments_count")),
                tags=tags,
            )
    LOGGER.info(f"Finished parsing file downloaded from: {url} . There were {counter} nodes.")


def changesets_between_sequences(
    start_sequence: Union[str, int],
    end_sequence: Union[str, int],
    replication_url: str = REPLICATION_CHANGESETS_URL,
) -> Generator[Changeset, None, None]:
    """Download and parse all changes since provided sequence number. Yields Changesets."""

    if type(start_sequence) == str:
        start_sequence = replication_sequence_to_int(start_sequence)
    if type(end_sequence) == str:
        end_sequence = replication_sequence_to_int(end_sequence)

    for seq in range(start_sequence, end_sequence + 1):
        osc_url = urllib.parse.urljoin(replication_url, f"{format_replication_sequence(seq)}.osm.gz")
        for changeset in download_and_parse_changeset_file(osc_url):
            yield changeset
