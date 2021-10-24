from dataclasses import dataclass
from typing import List, Optional

from common import database as db


@dataclass
class Process:
    name: str
    in_progress: bool
    start_time: str
    end_time: str
    number_of_tiles_to_process: Optional[int]
    abbreviated_name: str
    last_status: str

    def as_dict(self):
        return {
            'name': self.name,
            'in_progress': self.in_progress,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'no_of_tiles_to_process': self.number_of_tiles_to_process,
            'abbr_name': self.abbreviated_name,
            'last_status': self.last_status,
        }


def status() -> List[Process]:
    return db.data_from_db(db.QUERIES['processes'], row_as=Process, bypass_lock=True)
