"""Cross-source entity linking hooks.

Post-load Cypher scripts that create relationships between entities
from different data sources using name matching and shared identifiers.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)

# Link lobbyists to politicians by matching PublicOfficial names to TDOrSenator names
LINK_OFFICIALS_TO_POLITICIANS = """
MATCH (po:PublicOfficial)
MATCH (td:TDOrSenator)
WHERE toLower(po.name) = toLower(td.name)
MERGE (po)-[:SAME_AS]->(td)
"""

# Link lobbyist companies to CRO companies via company_number
# (This is handled by the lobbying pipeline's REPRESENTS_COMPANY rel,
# but this hook catches any we missed)
LINK_LOBBYISTS_TO_COMPANIES = """
MATCH (l:Lobbyist)
WHERE l.company_number IS NOT NULL AND l.company_number <> ''
MATCH (c:Company {company_number: l.company_number})
MERGE (l)-[:REPRESENTS_COMPANY]->(c)
"""

# Link charities to their CLG companies via company_number
# (Also handled by charities pipeline, this is a safety net)
LINK_CHARITIES_TO_COMPANIES = """
MATCH (ch:Charity)
WHERE ch.company_number IS NOT NULL AND ch.company_number <> ''
MATCH (c:Company {company_number: ch.company_number})
MERGE (ch)-[:REGISTERED_AS]->(c)
"""

ALL_HOOKS = [
    ("link_officials_to_politicians", LINK_OFFICIALS_TO_POLITICIANS),
    ("link_lobbyists_to_companies", LINK_LOBBYISTS_TO_COMPANIES),
    ("link_charities_to_companies", LINK_CHARITIES_TO_COMPANIES),
]


def run_all_hooks(
    driver: Driver,
    database: str | None = None,
) -> dict[str, int]:
    """Execute all cross-source linking hooks.

    Returns a dict of hook_name -> number of relationships created/merged.
    """
    results: dict[str, int] = {}
    for name, query in ALL_HOOKS:
        try:
            with driver.session(database=database) as session:
                result = session.run(query)
                summary = result.consume()
                count = summary.counters.relationships_created
                results[name] = count
                logger.info("Hook %s: %d relationships created", name, count)
        except Exception:
            logger.exception("Hook %s failed", name)
            results[name] = -1
    return results
