"""Tests for Irish address parsing."""

from __future__ import annotations

from ieacc_etl.transforms.address_parsing import (
    build_full_address,
    extract_county,
    extract_eircode,
)


class TestExtractCounty:
    def test_county_in_address4(self) -> None:
        assert extract_county(addr4="Dublin, Ireland") == "Dublin"

    def test_county_with_co_prefix(self) -> None:
        assert extract_county(addr4="Co. Cork") == "Cork"

    def test_county_in_address3(self) -> None:
        assert extract_county(addr3="Co. Galway", addr4="Ireland") == "Galway"

    def test_county_uppercase(self) -> None:
        assert extract_county(addr4="CLARE, IRELAND") == "Clare"

    def test_all_none(self) -> None:
        assert extract_county() is None

    def test_no_county_found(self) -> None:
        assert extract_county(addr1="123 Main Street") is None

    def test_county_prefix_variations(self) -> None:
        assert extract_county(addr4="County Kerry") == "Kerry"
        assert extract_county(addr4="Co Louth") == "Louth"

    def test_louth_from_address(self) -> None:
        assert extract_county(addr4="Louth, Ireland") == "Louth"


class TestExtractEircode:
    def test_standard_eircode(self) -> None:
        assert extract_eircode(addr4="D02 AF30") == "D02 AF30"

    def test_eircode_without_space(self) -> None:
        assert extract_eircode(addr4="T12Y037") == "T12 Y037"

    def test_eircode_in_address_line(self) -> None:
        result = extract_eircode(addr4="Dublin, Ireland, D01 W2X8")
        assert result == "D01 W2X8"

    def test_no_eircode(self) -> None:
        assert extract_eircode(addr1="123 Main Street") is None

    def test_all_none(self) -> None:
        assert extract_eircode() is None

    def test_eircode_lowercase_normalised(self) -> None:
        assert extract_eircode(addr4="v95 x2k3") == "V95 X2K3"


class TestBuildFullAddress:
    def test_all_fields(self) -> None:
        result = build_full_address("12 Grafton St", "Floor 2", "Dublin 2", "Dublin, Ireland")
        assert result == "12 Grafton St, Floor 2, Dublin 2, Dublin, Ireland"

    def test_some_empty(self) -> None:
        result = build_full_address("12 Grafton St", None, "", "Dublin, Ireland")
        assert result == "12 Grafton St, Dublin, Ireland"

    def test_all_empty(self) -> None:
        assert build_full_address() == ""

    def test_strips_whitespace(self) -> None:
        result = build_full_address("  12 Main St  ", None, "  Cork  ")
        assert result == "12 Main St, Cork"
