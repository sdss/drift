#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-07-18
# @Filename: test_adaptors.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pytest

from drift import adaptors


def test_ee_temp():

    assert adaptors.t_dwyer(0) == (-30, "degC")
    assert adaptors.t_dwyer(2 ** 15 - 1)[0] == 70


def test_ee_rh():

    assert adaptors.rh_dwyer(0) == (0, "percent")
    assert adaptors.rh_dwyer(2 ** 15 - 1)[0] == 100


def test_rtd():

    assert adaptors.rtd(1) == (0.1, "degC")
    assert adaptors.rtd(8510)[0] == -5702.5


def test_rtd10():

    assert adaptors.rtd10(101) == (10.1, "degC")


@pytest.mark.parametrize(
    "raw,v_min,v_max,expected",
    [(0, 0, 30, 0), (32760, 0, 30, 30)],
)
def test_voltage(raw, v_min, v_max, expected):

    assert adaptors.voltage(raw, v_min, v_max) == (expected, "V")


@pytest.mark.parametrize(
    "raw,min,max,range_min,range_max,expected",
    [
        (500, 0, 100, 0, 2 ** 15 - 1, 1.53),
        (6552, 2, 16, 3276, 16380, 5.5),
    ],
)
def test_linear(raw, min, max, range_min, range_max, expected):

    expected_value = pytest.approx(expected, abs=0.01)
    assert adaptors.linear(raw, min, max, range_min, range_max)[0] == expected_value


@pytest.mark.parametrize("raw_value,expected", [(16000, 48.83), (1023 * 32, 99.9)])
def test_pwd(raw_value, expected):

    expected_value = pytest.approx(expected, abs=0.01)
    assert adaptors.pwd(raw_value)[0] == expected_value


@pytest.mark.parametrize(
    "raw_value,meter_gain,expected",
    [(3276, 1, 0), (16380, 4, 16)],
)
def test_flow(raw_value, meter_gain, expected):

    expected_value = pytest.approx(expected, abs=0.01)
    assert adaptors.flow(raw_value, meter_gain)[0] == expected_value
