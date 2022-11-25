import logging
import urllib.parse

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import floor
from typing import Union

from dags.utils import send_request

LOGGER = logging.getLogger(__name__)

REPLICATION_MINUTE_URL = "https://planet.osm.org/replication/minute/"
REPLICATION_HOUR_URL = "https://planet.osm.org/replication/hour/"
REPLICATION_DAY_URL = "https://planet.osm.org/replication/day/"
REPLICATION_CHANGESETS_URL = "https://planet.osm.org/replication/changesets/"


@dataclass(frozen=True)
class ReplicationSequence:
    timestamp: datetime
    number: int
    formatted: str


def format_replication_sequence(sequence: Union[int, str]) -> str:
    """Formats sequence number to format with slashes (how the files are separated into folders in the server).
    E.g.: 1234567 -> 001/234/567"""

    seq = str(sequence)
    if len(seq) < 7:
        return f"000/{seq[1:4]}/{seq[4:7]}"
    elif len(seq) == 11:
        return seq
    else:
        return f"{seq[0].zfill(3)}/{seq[1:4]}/{seq[4:7]}"


def replication_sequence_to_int(sequence: str) -> int:
    """Convert formatted sequence to integer. E.g.: 001/222/333 -> 1222333."""
    return int(sequence.replace("/", ""))


def get_replication_sequence(url: str) -> ReplicationSequence:
    """Helper method that downloads state txt file from given url and parses out sequence number and timestamp."""

    response = send_request(url)
    data = response.text.splitlines()
    seq = data[1].split("=")[1]
    ts = data[2].split("=")[1]
    dt = datetime.fromisoformat(ts.replace("\\", "").replace("Z", ""))

    return ReplicationSequence(timestamp=dt, number=int(seq), formatted=format_replication_sequence(seq))


def find_newest_replication_sequence(replication_url: str = REPLICATION_MINUTE_URL) -> ReplicationSequence:
    """Checks what's the newest sequence number in OSM replication log."""
    url = urllib.parse.urljoin(replication_url, "state.txt")
    return get_replication_sequence(url)


def estimated_replication_sequence(delta: timedelta) -> ReplicationSequence:
    """Estimate sequence number based on newest sequence number and timedelta.
    Timedelta should be created with negative values."""

    newest_replication_sequence = find_newest_replication_sequence()
    minutes = floor(delta.total_seconds() / 60)
    new_seq_num = newest_replication_sequence.number + minutes
    new_seq_formatted = format_replication_sequence(new_seq_num)
    new_seq_ts = newest_replication_sequence.timestamp + delta

    return ReplicationSequence(timestamp=new_seq_ts, number=new_seq_num, formatted=new_seq_formatted)
