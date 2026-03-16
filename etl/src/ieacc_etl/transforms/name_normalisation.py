"""Irish name and company name normalisation."""

from __future__ import annotations

import re

# Company suffix patterns to standardise
# Order matters: longer patterns must come before shorter ones
_COMPANY_SUFFIXES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bPUBLIC LIMITED COMPANY\b", re.IGNORECASE), "PLC"),
    (re.compile(r"\bCOMPANY LIMITED BY GUARANTEE\b", re.IGNORECASE), "CLG"),
    (re.compile(r"\bDESIGNATED ACTIVITY COMPANY\b", re.IGNORECASE), "DAC"),
    (re.compile(r"\bCUIDACHTA PHOIBLÍ THEORANTA\b", re.IGNORECASE), "CPT"),
    (re.compile(r"\bUNLIMITED COMPANY\b", re.IGNORECASE), "UC"),
    (re.compile(r"\bLIMITED\b", re.IGNORECASE), "LTD"),
    (re.compile(r"\bTEORANTA\b", re.IGNORECASE), "TEO"),
]

# Mc/Mac prefix patterns
_MC_PATTERN = re.compile(r"\b(Mc|Mac)([a-z])", re.UNICODE)


def normalise_company_name(name: str | None) -> str:
    """Normalise an Irish company name.

    - Strip whitespace
    - Title case
    - Standardise suffixes (LIMITED -> LTD, etc.)
    """
    if not name:
        return ""

    result = name.strip()

    for pattern, replacement in _COMPANY_SUFFIXES:
        result = pattern.sub(replacement, result)

    # Collapse multiple spaces
    result = re.sub(r"\s+", " ", result).strip()

    return result


def normalise_person_name(name: str | None) -> str:
    """Normalise an Irish person name.

    - Strip whitespace
    - Title case with Mc/Mac handling
    - Handle O' prefixes
    """
    if not name:
        return ""

    result = name.strip().title()

    # Fix Mc/Mac capitalisation: "Mcnamara" -> "McNamara"
    result = _MC_PATTERN.sub(lambda m: m.group(1) + m.group(2).upper(), result)

    # Fix O' prefix: "O'brien" -> "O'Brien"
    result = re.sub(r"\bO'([a-z])", lambda m: "O'" + m.group(1).upper(), result)

    return result


def generate_person_id(name: str, context: str = "") -> str:
    """Generate a deterministic person ID from name + context.

    Context can be company_number, appointment date, etc.
    This is NOT a universal identifier — it's a best-effort
    deduplication key within a single source.
    """
    key = f"{normalise_person_name(name).lower()}|{context}".strip("|")
    # Simple hash-based ID
    import hashlib

    return hashlib.sha256(key.encode()).hexdigest()[:16]
