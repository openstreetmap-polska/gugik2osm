from pathlib import Path
from typing import Generator

this_file_path = Path(__file__)
codes_county_path = this_file_path.parent / "codes_county.txt"
codes_voivodeship_path = this_file_path.parent / "codes_voivodeship.txt"


def county_codes() -> Generator[str, None, None]:
    with open(codes_county_path, "r", encoding="utf-8") as fo:
        for line in fo:
            yield line.strip()


def voivodeship_codes() -> Generator[str, None, None]:
    with open(codes_voivodeship_path, "r", encoding="utf-8") as fo:
        for line in fo:
            yield line.strip()
