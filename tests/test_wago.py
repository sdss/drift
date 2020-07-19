#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-07-18
# @Filename: test_wago.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pytest

from wago import WAGO


pytestmark = pytest.mark.asyncio


async def test_wago(default_wago):

    assert isinstance(default_wago, WAGO)

    assert len(default_wago.modules) == 2

    assert len(default_wago['module1'].devices) == 1
    assert default_wago['module1'].mode == 'input'
    assert default_wago['module1'].channels == 4

    assert len(default_wago['module2'].devices) == 1
    assert default_wago['module2'].mode == 'output'
    assert default_wago['module2'].channels == 4


async def test_wago_read(default_wago):

    assert await default_wago.get_device('temp1').read(adapt=False) == 100

    value, units = await default_wago.get_device('temp1').read()
    assert value == pytest.approx(-29.69, 0.01)
    assert units == 'degC'


async def test_wago_write(default_wago):

    await default_wago.get_device('relay1').read() == (False, None)
    await default_wago.get_device('relay1').write(True)
    await default_wago.get_device('relay1').read() == (True, None)


async def test_add_known_module(wago):

    wago.add_module('module', 40001, model='750-497')

    assert wago['module'].channels == 8
    assert wago['module'].mode == 'input'