#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-07-18
# @Filename: test_wago.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import types
from unittest.mock import patch

import pytest
from yaml import SafeLoader, load

from wago import WAGO, Relay

from .conftest import AsyncMock, MagicMock


pytestmark = pytest.mark.asyncio


config = """
address: 10.1.10.1
port: 502
modules:
    module1:
        model: "750-530"
        address: 40513
        devices:
            "relay1":
                channel: 0
                type: relay
                relay_type: "NO"

"""


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

    value, units = await default_wago.get_device('module1.temp1').read()
    assert value == pytest.approx(-29.69, 0.01)
    assert units == 'degC'


async def test_wago_write(default_wago):

    assert (await default_wago.get_device('relay1').read()) == ('closed', None)
    await default_wago.get_device('relay1').write(True)
    assert (await default_wago.get_device('relay1').read()) == ('open', None)


async def test_add_known_module(wago):

    wago.add_module('module', 40001, model='750-497')

    assert wago['module'].channels == 8
    assert wago['module'].mode == 'input'


async def test_remove_device(default_wago):

    assert default_wago['module1'].remove_device('temp1') is not None

    with pytest.raises(ValueError):
        default_wago.get_device('temp1')


async def test_from_config(tmp_path):

    config_path = tmp_path / 'test_config.yaml'
    config_path.write_text(config)

    wago = WAGO.from_config(str(config_path))

    assert 'module1' in wago.modules
    assert wago.get_device('relay1').relay_type == 'NO'


async def test_relay(default_wago):

    relay = default_wago.get_device('relay1')

    assert (await relay.read())[0] == 'closed'

    await relay.switch()
    assert (await relay.read())[0] == 'open'

    await relay.cycle(delay=0.01)
    assert (await relay.read())[0] == 'open'

    await relay.close()
    assert (await relay.read())[0] == 'closed'

    await relay.open()
    assert (await relay.read())[0] == 'open'


async def test_relay_no(wago):

    wago.add_module('module1', 40001, mode='output', channels=4)
    relay = wago['module1'].add_device('relay_no', 0,
                                       device_class=Relay,
                                       relay_type='NO')

    wago._state[40001] = False

    assert (await relay.read())[0] == 'open'

    await relay.close()
    assert (await relay.read())[0] == 'closed'

    await relay.open()
    assert (await relay.read())[0] == 'open'


async def test_adaptor_tuple():

    config_dict = load(config, Loader=SafeLoader)

    relay = config_dict['modules']['module1']['devices']['relay1']
    del relay['type']
    del relay['relay_type']
    relay['adaptor'] = [(False, 'open'), (True, 'closed')]
    relay['coils'] = True

    wago = WAGO.from_config(config_dict)

    wago.client.connect = AsyncMock()
    wago.client.stop = AsyncMock()
    wago.client.connected = True

    wago.client.protocol = AsyncMock()

    response = types.SimpleNamespace()
    response.function_code = 0
    response.bits = [False]

    wago.client.protocol.read_coils = AsyncMock(return_value=response)

    assert (await wago['module1']['relay1'].read())[0] == 'open'


async def test_read_category(default_wago):

    default_wago['module2'].add_device('relay_no', 1,
                                       device_class=Relay,
                                       relay_type='NO',
                                       category='relay')

    default_wago._state[40102] = False

    values = await default_wago.read_category('relay')

    assert len(values) == 2

    assert values['module2.relay1'][0] == 'closed'
    assert values['module2.relay_no'][0] == 'open'


async def test_custom_adaptor(default_wago):

    with patch('wago.adaptors.my_adaptor', create=True,
               new=MagicMock(return_value=(100, 'degF'))):

        default_wago['module1'].add_device('device2', 1,
                                           adaptor='wago.adaptors:my_adaptor')
    default_wago._state[40002] = 5

    device2 = default_wago.get_device('device2')

    assert await device2.read(adapt=False) == 5
    assert (await device2.read()) == (100, 'degF')


async def test_invalid_model(wago):

    with pytest.raises(WAGOError):
        wago.add_module('unknown_module', 42000, model='bad_model')
