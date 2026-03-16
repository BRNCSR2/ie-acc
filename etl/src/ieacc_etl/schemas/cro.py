"""Pandera schema for CRO company data."""

from __future__ import annotations

import pandera as pa

cro_company_schema = pa.DataFrameSchema(  # type: ignore[no-untyped-call]
    {
        "company_num": pa.Column(int, nullable=False, coerce=True),
        "company_name": pa.Column(str, nullable=False),
        "company_status": pa.Column(str, nullable=True),
        "company_type": pa.Column(str, nullable=True),
        "company_reg_date": pa.Column(str, nullable=True),
        "county": pa.Column(str, nullable=True),
        "address": pa.Column(str, nullable=True),
        "eircode": pa.Column(str, nullable=True),
    },
    coerce=True,
)
