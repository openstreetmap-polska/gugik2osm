from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .. import database as db


@dataclass
class Update:
    dataset: str
    created_at: Optional[str]
    area: dict
    changesets: dict


def latest_updates(timestamp: datetime) -> List[Update]:
    return db.data_from_db(db.QUERIES['latest_updates'], {'ts': timestamp}, row_as=Update)
