"""Tests for Irish name normalisation."""

from __future__ import annotations

from ieacc_etl.transforms.name_normalisation import (
    generate_person_id,
    normalise_company_name,
    normalise_person_name,
)


class TestNormaliseCompanyName:
    def test_strips_whitespace(self) -> None:
        assert normalise_company_name("  TEST LTD  ") == "TEST LTD"

    def test_limited_to_ltd(self) -> None:
        result = normalise_company_name("GREENFIELD CONSTRUCTION LIMITED")
        assert result == "GREENFIELD CONSTRUCTION LTD"

    def test_public_limited_company_to_plc(self) -> None:
        result = normalise_company_name("CELTIC WASTE SOLUTIONS PUBLIC LIMITED COMPANY")
        assert result == "CELTIC WASTE SOLUTIONS PLC"

    def test_designated_activity_company_to_dac(self) -> None:
        result = normalise_company_name("ATLANTIC CONSULTING DESIGNATED ACTIVITY COMPANY")
        assert result == "ATLANTIC CONSULTING DAC"

    def test_company_limited_by_guarantee_to_clg(self) -> None:
        result = normalise_company_name("BURREN HERITAGE COMPANY LIMITED BY GUARANTEE")
        assert result == "BURREN HERITAGE CLG"

    def test_teoranta_to_teo(self) -> None:
        assert normalise_company_name("SÉAMUS Ó'BRIAIN TEORANTA") == "SÉAMUS Ó'BRIAIN TEO"

    def test_empty_and_none(self) -> None:
        assert normalise_company_name("") == ""
        assert normalise_company_name(None) == ""

    def test_collapses_multiple_spaces(self) -> None:
        assert normalise_company_name("TEST   COMPANY   LTD") == "TEST COMPANY LTD"


class TestNormalisePersonName:
    def test_title_case(self) -> None:
        assert normalise_person_name("SEAN O'BRIEN") == "Sean O'Brien"

    def test_mc_prefix(self) -> None:
        assert normalise_person_name("CIARAN MCNAMARA") == "Ciaran McNamara"

    def test_mac_prefix(self) -> None:
        assert normalise_person_name("AOIFE MACCARTHY") == "Aoife MacCarthy"

    def test_o_apostrophe(self) -> None:
        assert normalise_person_name("NIAMH O'SULLIVAN") == "Niamh O'Sullivan"

    def test_empty_and_none(self) -> None:
        assert normalise_person_name("") == ""
        assert normalise_person_name(None) == ""

    def test_strips_whitespace(self) -> None:
        assert normalise_person_name("  JOHN MURPHY  ") == "John Murphy"


class TestGeneratePersonId:
    def test_deterministic(self) -> None:
        id1 = generate_person_id("Sean O'Brien", "100001")
        id2 = generate_person_id("Sean O'Brien", "100001")
        assert id1 == id2

    def test_different_context_different_id(self) -> None:
        id1 = generate_person_id("Sean O'Brien", "100001")
        id2 = generate_person_id("Sean O'Brien", "100002")
        assert id1 != id2

    def test_returns_16_char_hex(self) -> None:
        result = generate_person_id("Test Name")
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)
