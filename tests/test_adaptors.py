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
