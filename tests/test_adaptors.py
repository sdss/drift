#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-07-18
# @Filename: test_adaptors.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from drift import adaptors


def test_ee_temp():

    assert adaptors.ee_temp(0) == (-30, "degC")
    assert adaptors.ee_temp(2 ** 15 - 1)[0] == 70


def test_ee_rh():

    assert adaptors.ee_rh(0) == (0, "percent")
    assert adaptors.ee_rh(2 ** 15 - 1)[0] == 100


def test_rtd():

    assert adaptors.rtd(1) == (0.1, "degC")
    assert adaptors.rtd(8510)[0] == -5702.5
