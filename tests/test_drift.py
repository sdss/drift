#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-07-18
# @Filename: test_drift.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import types
from unittest.mock import patch

import pytest
from yaml import SafeLoader, load

from drift import Drift, Relay, adaptors
from drift.exceptions import DriftError, DriftUserWarning

from .conftest import AsyncMock, MagicMock


pytestmark = pytest.mark.asyncio


config = """
address: 10.1.10.1
port: 502
modules:
    module1:
        model: "750-530"
        devices:
            "relay1":
                address: 40513
                mode: coil
                type: relay
                relay_type: "NO"

"""


async def test_drift(default_drift):

    assert isinstance(default_drift, Drift)

    assert len(default_drift.modules) == 2

    assert len(default_drift["module1"].devices) == 1
    assert default_drift["module1"].mode == "input_register"
    assert default_drift["module1"].channels == 4

    assert len(default_drift["module2"].devices) == 1
    assert default_drift["module2"].channels == 4


async def test_drift_read(default_drift):

    assert await default_drift.get_device("temp1").read(adapt=False) == 100

    value, units = await default_drift.get_device("module1.temp1").read()
    assert value == pytest.approx(-29.69, 0.01)
    assert units == "degC"


async def test_drift_read_device(default_drift):

    assert await default_drift.read_device("temp1", adapt=False) == 100
    assert await default_drift.read("temp1", adapt=False) == 100


async def test_drift_write(default_drift):

    assert (await default_drift.get_device("relay1").read()) == ("closed", None)
    await default_drift.get_device("relay1").write(True)
    assert (await default_drift.get_device("relay1").read()) == ("open", None)


async def test_add_known_module(drift):

    drift.add_module("module", model="750-497")

    assert drift["module"].channels == 8
    assert drift["module"].mode == "input_register"


async def test_remove_device(default_drift):

    assert default_drift["module1"].remove_device("temp1") is not None

    with pytest.raises(ValueError):
        default_drift.get_device("temp1")


async def test_from_config(tmp_path):

    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(config)

    drift = Drift.from_config(str(config_path))

    assert "module1" in drift.modules
    assert drift.get_device("relay1").relay_type == "NO"  # type: ignore


async def test_relay(default_drift):

    relay = default_drift.get_device("relay1")

    assert (await relay.read())[0] == "closed"

    await relay.switch()
    assert (await relay.read())[0] == "open"

    await relay.cycle(delay=0.01)
    assert (await relay.read())[0] == "open"

    await relay.close()
    assert (await relay.read())[0] == "closed"

    await relay.open()
    assert (await relay.read())[0] == "open"


async def test_relay_no(drift):

    drift.add_module("module1", mode="coil", channels=4)
    relay = drift["module1"].add_device(
        "relay_no",
        40001,
        device_class=Relay,
        relay_type="NO",
    )

    drift._state[40001] = False

    assert (await relay.read())[0] == "open"

    await relay.close()
    assert (await relay.read())[0] == "closed"

    await relay.open()
    assert (await relay.read())[0] == "open"


async def test_adaptor_tuple():

    config_dict = load(config, Loader=SafeLoader)

    relay = config_dict["modules"]["module1"]["devices"]["relay1"]
    del relay["type"]
    del relay["relay_type"]
    relay["adaptor"] = [(False, "open"), (True, "closed")]
    relay["mode"] = "coil"

    drift = Drift.from_config(config_dict)

    drift.client.connect = AsyncMock()
    drift.client.stop = AsyncMock()
    drift.client.connected = True

    drift.client.protocol = AsyncMock()

    response = types.SimpleNamespace()
    response.function_code = 0
    response.bits = [False]

    drift.client.protocol.read_coils = AsyncMock(return_value=response)

    assert (await drift["module1"]["relay1"].read())[0] == "open"


async def test_read_category(default_drift):

    default_drift["module2"].add_device(
        "relay_no",
        40102,
        device_class=Relay,
        relay_type="NO",
        category="relay",
    )

    default_drift._state[40102] = False

    values = await default_drift.read_category("relay")

    assert len(values) == 2

    assert values["module2.relay1"][0] == "closed"
    assert values["module2.relay_no"][0] == "open"


async def test_custom_adaptor(default_drift):

    with patch(
        "drift.adaptors.my_adaptor",
        create=True,
        new=MagicMock(return_value=(100, "degF")),
    ):

        default_drift["module1"].add_device(
            "device2", 40002, adaptor="drift.adaptors:my_adaptor"
        )
    default_drift._state[40002] = 5

    device2 = default_drift.get_device("device2")

    assert await device2.read(adapt=False) == 5
    assert (await device2.read()) == (100, "degF")


async def test_invalid_model(drift):

    with pytest.raises(DriftError):
        drift.add_module("unknown_module", model="bad_model")


async def test_add_device(default_drift):

    module2 = default_drift["module2"]
    relay = Relay(module2, "relay2", 40003, relay_type="NO")
    module2.add_device(relay)

    assert default_drift.get_device("relay2").relay_type == "NO"


async def test_get_device_case_insensitive(default_drift):

    assert default_drift.get_device("TEmP1") is not None


async def test_adaptor_extra_params(default_drift):

    dev = default_drift["module1"]["temp1"]
    dev.adaptor = adaptors.voltage
    dev._adaptor_extra_params = [0, 20, 10]

    dev.read(adapt=True) == (200, "V")


async def test_mismatch_mode(default_drift):

    with pytest.warns(DriftUserWarning) as w:
        default_drift.add_module("test", model="750-450", mode="coil")

    assert "mode 'coil' is different from default" in str(w[0].message)


async def test_mismatch_channels(default_drift):

    with pytest.warns(DriftUserWarning) as w:
        default_drift.add_module("test", model="750-450", channels=15)

    assert "number of channels 15 is different from default" in str(w[0].message)


async def test_module_bad_mode(default_drift):

    with pytest.raises(DriftError):
        default_drift.add_module("test", mode="bad_mode")


async def test_device_no_mode(default_drift):

    with pytest.raises(DriftError):
        default_drift["module2"].add_device("test", 40100)


async def test_device_bad_mode(default_drift):

    with pytest.raises(DriftError):
        default_drift["module2"].add_device("test", 40100, mode="aaa")


async def test_unknown_channels(default_drift):

    with pytest.raises(DriftError) as err:
        default_drift.add_module("test")

    assert "Cannot determine module number of channels." in str(err)


async def test_add_device_already_exists(default_drift):

    with pytest.raises(DriftError) as err:
        default_drift["module1"].add_device("temp1", 40100)

    assert "already exists in module" in str(err)


async def test_relay_holding_register(default_drift):

    mod = default_drift.add_module("module3", channels=4)
    dev = mod.add_device("relayH", 40501, mode="holding_register", channel=3)

    await dev.write(True)

    assert (await dev.read())[0] is True
