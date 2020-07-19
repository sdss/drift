#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-07-18
# @Filename: conftest.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import sys
import types
from functools import partial
from unittest.mock import MagicMock

import pytest

from wago import WAGO, Relay


if sys.version_info.major < 3:
    raise ValueError('Python 2 is not supported.')
if sys.version_info.minor <= 7:
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock


async def read_mocker(state, address, coil=False, count=1):

    response = types.SimpleNamespace()
    response.function_code = 0
    response.bits = []
    response.registers = []

    value = state[40001 + address]

    if coil:
        response.bits.append(value)
    else:
        response.registers.append(value)

    return response


async def write_mocker(state, address, value):

    response = types.SimpleNamespace()
    response.function_code = 0

    state[40001 + address] = value

    return response


@pytest.fixture
def wago():
    """A fixture for a mocked WAGO."""

    wago_instance = WAGO('localhost')

    wago_instance._state = {}
    state = wago_instance._state

    wago_instance.client.connect = AsyncMock()
    wago_instance.client.close = AsyncMock()
    wago_instance.client.connected = True

    # Make protocol a mock. Since we are also mocking connect, the protocol
    # never changes and remains a mock.
    wago_instance.client.protocol = AsyncMock()

    protocol = wago_instance.client.protocol

    protocol.read_input_registers = MagicMock(side_effect=partial(read_mocker,
                                                                  state,
                                                                  coil=False))
    protocol.read_coils = MagicMock(side_effect=partial(read_mocker,
                                                        state,
                                                        coil=True))
    protocol.write_coil = MagicMock(side_effect=partial(write_mocker,
                                                        state))
    protocol.write_register = MagicMock(side_effect=partial(write_mocker,
                                                            state))

    yield wago_instance


@pytest.fixture
def default_wago(wago):
    """A WAGO with some default devices connected."""

    module1 = wago.add_module('module1', 40001, mode='input', channels=4)
    module1.add_device('temp1', 0, adaptor='ee_temp')

    module2 = wago.add_module('module2', 40101, mode='output', channels=4)
    module2.add_device('relay1', 0, device_class=Relay)

    wago._state[40001] = 100
    wago._state[40101] = False

    yield wago
