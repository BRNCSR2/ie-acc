"""Irish address parsing utilities."""

from __future__ import annotations

import math
import re

# All 26 counties + Dublin (which appears as just "Dublin" or "Co. Dublin")
COUNTIES = [
    "Carlow", "Cavan", "Clare", "Cork", "Donegal", "Dublin",
    "Galway", "Kerry", "Kildare", "Kilkenny", "Laois", "Leitrim",
    "Limerick", "Longford", "Louth", "Mayo", "Meath", "Monaghan",
    "Offaly", "Roscommon", "Sligo", "Tipperary", "Waterford",
    "Westmeath", "Wexford", "Wicklow",
]

_COUNTY_PATTERN = re.compile(
    r"(?:(?:Co(?:unty)?\.?\s+)|(?:,\s*))(" + "|".join(COUNTIES) + r")\b",
    re.IGNORECASE,
)

_EIRCODE_PATTERN = re.compile(
    r"\b([A-Z]\d{2})\s*([A-Z0-9]{4})\b",
    re.IGNORECASE,
)


def _is_valid_str(val: object) -> bool:
    """Check if a value is a non-empty string (handles NaN from pandas)."""
    if val is None:
        return False
    if isinstance(val, float) and math.isnan(val):
        return False
    if not isinstance(val, str):
        return False
    return bool(val.strip())


def extract_county(
    addr1: str | None = None,
    addr2: str | None = None,
    addr3: str | None = None,
    addr4: str | None = None,
) -> str | None:
    """Extract the county from Irish address fields.

    CRO data typically has county in address_4 as "COUNTY, Ireland".
    Falls back to searching all address fields.
    """
    # Search address_4 first (most likely location for county)
    for addr in [addr4, addr3, addr2, addr1]:
        if not _is_valid_str(addr):
            continue
        match = _COUNTY_PATTERN.search(str(addr))
        if match:
            return match.group(1).title()

    # Direct match for county names without prefix
    for addr in [addr4, addr3, addr2, addr1]:
        if not _is_valid_str(addr):
            continue
        upper = str(addr).strip().upper()
        for county in COUNTIES:
            if county.upper() in upper:
                return county

    return None


def extract_eircode(
    addr1: str | None = None,
    addr2: str | None = None,
    addr3: str | None = None,
    addr4: str | None = None,
) -> str | None:
    """Extract an Eircode from address fields.

    Eircodes follow the pattern: routing key (letter + 2 digits) + space + 4 alphanumeric.
    Example: D02 AF30, T12 Y037
    """
    for addr in [addr4, addr3, addr2, addr1]:
        if not _is_valid_str(addr):
            continue
        match = _EIRCODE_PATTERN.search(str(addr))
        if match:
            return f"{match.group(1).upper()} {match.group(2).upper()}"

    return None


def build_full_address(
    addr1: str | None = None,
    addr2: str | None = None,
    addr3: str | None = None,
    addr4: str | None = None,
) -> str:
    """Combine address fields into a single string."""
    parts = [
        str(a).strip()
        for a in [addr1, addr2, addr3, addr4]
        if _is_valid_str(a)
    ]
    return ", ".join(parts)
