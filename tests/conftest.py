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

from drift import Drift, Relay


if sys.version_info.major < 3:
    raise ValueError("Python 2 is not supported.")
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
def drift():
    """A fixture for a mocked Drift."""

    drift_instance = Drift("localhost")

    drift_instance._state = {}  # type: ignore
    state = drift_instance._state  # type: ignore

    drift_instance.client.connect = AsyncMock()  # type: ignore
    drift_instance.client.close = AsyncMock()  # type: ignore
    drift_instance.client.connected = True

    # Make protocol a mock. Since we are also mocking connect, the protocol
    # never changes and remains a mock.
    drift_instance.client.protocol = AsyncMock()

    protocol = drift_instance.client.protocol

    protocol.read_input_registers = MagicMock(
        side_effect=partial(read_mocker, state, coil=False)
    )
    protocol.read_coils = MagicMock(side_effect=partial(read_mocker, state, coil=True))
    protocol.write_coil = MagicMock(side_effect=partial(write_mocker, state))
    protocol.write_register = MagicMock(side_effect=partial(write_mocker, state))

    yield drift_instance


@pytest.fixture
def default_drift(drift):
    """A Drift with some default devices connected."""

    module1 = drift.add_module("module1", 40001, mode="input", channels=4)
    module1.add_device("temp1", 0, adaptor="ee_temp")

    module2 = drift.add_module("module2", 40101, mode="output", channels=4)
    module2.add_device("relay1", 0, device_class=Relay, category="relay")

    drift._state[40001] = 100
    drift._state[40101] = False

    yield drift
