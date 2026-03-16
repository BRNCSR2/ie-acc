"""Pipeline registry. Import and register all pipelines here."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ieacc_etl.base import Pipeline

from ieacc_etl.pipelines.charities import CharitiesPipeline
from ieacc_etl.pipelines.cro import CROPipeline
from ieacc_etl.pipelines.epa import EPAPipeline
from ieacc_etl.pipelines.etenders import ETendersPipeline
from ieacc_etl.pipelines.lobbying import LobbyingPipeline
from ieacc_etl.pipelines.oireachtas import OireachtasPipeline
from ieacc_etl.pipelines.ppr import PPRPipeline

PIPELINES: dict[str, type[Pipeline]] = {
    "cro": CROPipeline,
    "lobbying": LobbyingPipeline,
    "oireachtas": OireachtasPipeline,
    "charities": CharitiesPipeline,
    "etenders": ETendersPipeline,
    "epa": EPAPipeline,
    "ppr": PPRPipeline,
}
