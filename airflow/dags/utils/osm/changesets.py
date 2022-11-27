import bz2
import gzip
import json
import logging
import urllib.parse
import xml.dom.pulldom
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Generator, Union, Optional
from xml.dom.minidom import Element

from .replication import (
    ReplicationSequence,
    format_replication_sequence,
    REPLICATION_CHANGESETS_URL,
    replication_sequence_to_int,
)
from .. import send_request, parse_bool

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Changeset:
    id: int
    created_at: datetime
    closed_at: Optional[datetime]
    open: bool
    num_changes: int
    user: Optional[str]
    uid: Optional[int]
    min_lat: Optional[float]
    max_lat: Optional[float]
    min_lon: Optional[float]
    max_lon: Optional[float]
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
        data["tags"] = json.dumps(data["tags"])
        return data


def get_changeset_replication_sequence(url: str) -> ReplicationSequence:
    """Helper method that download state yaml file from given url and parses our sequence number and timestamp."""

    response = send_request(url)
    data = response.text.splitlines()
    ts = data[1].split(": ")[1]
    ts_components = ts.split(" ")
    ts_fixed = f"{ts_components[0]} {ts_components[1][:-3]}{ts_components[2]}"
    seq = int(data[2].split(": ")[1])
    dt = datetime.fromisoformat(ts_fixed)

    return ReplicationSequence(timestamp=dt, number=seq, formatted=format_replication_sequence(seq))


def find_newest_changeset_replication_sequence(
    replication_url: str = REPLICATION_CHANGESETS_URL
) -> ReplicationSequence:
    """Checks what's the newest changeset sequence number in OSM replication log."""
    url = urllib.parse.urljoin(replication_url, "state.yaml")
    return get_changeset_replication_sequence(url)


def parse_xml_file(file: Union[gzip.GzipFile, bz2.BZ2File]) -> Generator[Changeset, None, None]:
    LOGGER.info("Parsing XML...")
    event_stream = xml.dom.pulldom.parse(file)
    counter = 0
    for event, element in event_stream:
        element: Element = element  # just for typing
        if event == xml.dom.pulldom.START_ELEMENT and element.tagName == "changeset":
            counter += 1
            event_stream.expandNode(element)
            tags = {}
            for child in element.childNodes:
                child: Element = child  # for typing
                if type(child) == Element and child.tagName == "tag":
                    tags[child.getAttribute("k")] = child.getAttribute("v")
            created_at = element.getAttribute("created_at")
            closed_at = element.getAttribute("closed_at")
            min_lat = element.getAttribute("min_lat")
            max_lat = element.getAttribute("max_lat")
            min_lon = element.getAttribute("min_lon")
            max_lon = element.getAttribute("max_lon")
            user = element.getAttribute("user")
            uid = element.getAttribute("uid")
            yield Changeset(
                id=int(element.getAttribute("id")),
                created_at=datetime.fromisoformat(created_at.replace("Z", "+00:00")),
                closed_at=datetime.fromisoformat(closed_at.replace("Z", "+00:00")) if closed_at else None,
                open=parse_bool(element.getAttribute("open")),
                num_changes=int(element.getAttribute("num_changes")),
                user=user if user != "" else None,
                uid=int(uid) if uid != "" else None,
                min_lat=float(min_lat) if min_lat != "" else None,
                max_lat=float(max_lat) if max_lat != "" else None,
                min_lon=float(min_lon) if min_lon != "" else None,
                max_lon=float(max_lon) if max_lon != "" else None,
                comments_count=int(element.getAttribute("comments_count")),
                tags=tags,
            )
            if counter % 10000 == 0:
                LOGGER.info(f"Processed: {counter} features.")
    LOGGER.info(f"Finished parsing file. There were {counter} changesets.")


def download_and_parse_changeset_file(url: str) -> Generator[Changeset, None, None]:
    """Downloads gzip compressed XML file from URL and parses out Changeset."""

    response = send_request(url)
    LOGGER.info("Decompressing...")
    xml_data = gzip.GzipFile(fileobj=BytesIO(response.content))
    for changeset in parse_xml_file(xml_data):
        yield changeset


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


def parse_full_changeset_file(file_path: Union[Path, str]) -> Generator[Changeset, None, None]:
    with bz2.BZ2File(file_path) as fp:
        LOGGER.info("Decompressing...")
        for changeset in parse_xml_file(fp):
            yield changeset
