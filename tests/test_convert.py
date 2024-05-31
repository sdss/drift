#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-05-30
# @Filename: test_convert.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import pytest

from drift import convert


@pytest.mark.parametrize(
    "data,msb_first,endianness,expected",
    [
        ([10, 20], True, "<", b"\x14\x00\n\x00"),
        ([10, 20], False, "<", b"\n\x00\x14\x00"),
    ],
)
def test_convert_data_to_string(
    data: list[int],
    msb_first: bool,
    endianness: str,
    expected: bytes,
):
    assert (
        convert.data_to_string(
            data,
            msb_first=msb_first,
            endianness=endianness,
        )
        == expected
    )


def test_convert_data_to_uint16():
    assert convert.data_to_uint16(0x1234, endianness=">") == 0x3412
    assert convert.data_to_uint16(0x1234, endianness="<") == 0x1234
    assert convert.data_to_uint16(0x1234) == 0x1234


def test_convert_data_to_uint32():
    assert convert.data_to_uint32((1, 2)) == 65538


def test_convert_data_to_int32():
    assert convert.data_to_int32((433, 2432)) == 28379520


def test_convert_data_to_float32():
    assert pytest.approx(convert.data_to_float32((16181, 30372)), abs=0.001) == 0.7089
