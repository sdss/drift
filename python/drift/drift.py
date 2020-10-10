#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-11-11
# @Filename: drift.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
import importlib
import warnings
from collections import defaultdict

from pymodbus.client.asynchronous.async_io import AsyncioModbusTcpClient
from yaml import SafeLoader, load

from . import adaptors, log
from .exceptions import DriftError, DriftUserWarning


__ALL__ = ['Device', 'Relay', 'Module', 'MODULES', 'Drift']


MODULES = {
    '750-450': {
        'mode': 'input',
        'channels': 4
    },
    '750-497': {
        'mode': 'input',
        'channels': 8
    },
    '750-530': {
        'mode': 'output',
        'channels': 8
    }
}


class CaseInsensitiveDict(dict):
    """A case insensitive dictionary from https://bit.ly/2ZHgTpq."""

    @classmethod
    def _k(cls, key):
        return key.lower() if isinstance(key, str) else key

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key):
        return super().__getitem__(self.__class__._k(key))

    def __setitem__(self, key, value):
        super().__setitem__(self.__class__._k(key), value)

    def __delitem__(self, key):
        return super().__delitem__(self.__class__._k(key))

    def __contains__(self, key):
        return super().__contains__(self.__class__._k(key))

    def pop(self, key, *args, **kwargs):
        return super().pop(self.__class__._k(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super().get(self.__class__._k(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super().setdefault(self.__class__._k(key), *args, **kwargs)

    def update(self, E={}, **F):
        super().update(self.__class__(E))
        super().update(self.__class__(**F))

    def _convert_keys(self):
        for k in list(self.keys()):
            v = super().pop(k)
            self.__setitem__(k, v)


class Module(object):
    """A Modbus module with some devices connected.

    Parameters
    ----------
    name : str
        A name to be associated with this module.
    drift : .Drift
        The instance of `.Drift` used to communicate with the modbus network.
    address : int
        The initial address associated with this module. In modbus, addresses
        start at 40001.
    model : str
        The Drift model for this module.
    mode : str
        Whether this is an ``input`` or ``output`` module. If not provided it
        will be determined from ``model``.
    channels : int
        The number of channels in this module. If not provided it will be
        determined from ``model``.
    description : str
        A description or comment for this module.

    """

    def __init__(self, name, drift, address, model=None, mode=None,
                 channels=None, description=''):

        self.name = name
        self.drift = drift
        self.address = address

        self.description = description

        self.model = model

        if self.model:
            if self.model in MODULES:
                default_mode = MODULES[self.model]['mode']
                default_channels = MODULES[self.model]['channels']
            else:
                raise DriftError(f'Unknown model {self.model!r}')
        else:
            default_mode = None
            default_channels = None

        if mode is not None:
            self.mode = mode
            if default_mode and default_mode != self.mode:
                warnings.warn(f'mode {self.mode!r} is different from '
                              f'default mode {default_mode!r} for model '
                              f'{self.model},', DriftUserWarning)
        else:
            if default_mode is None:
                raise DriftError('Cannot determine module mode.')
            self.mode = default_mode

        if self.mode not in ['input', 'output']:
            raise DriftError(f'Invalid mode {mode}.')

        if channels is not None:
            self.channels = channels
            if default_channels and default_channels != self.channels:
                warnings.warn(f'channels {self.channels!r} is different from '
                              f'default channels {default_channels!r} for '
                              f'model {self.model},', DriftUserWarning)
        else:
            if default_channels is None:
                raise DriftError('Cannot determine module channels.')
            self.channels = default_channels

        self.devices = CaseInsensitiveDict()

        log.info(f'Created module {self.name}@{self.address} with '
                 f'mode {self.mode} and {self.channels} channels.')

    def __repr__(self):
        return (f'<Module {self.name}@{self.address} (mode={self.mode!r}, '
                f'channels={self.channels}, n_devices={len(self.devices)})>')

    def __getitem__(self, name):
        """Gets a device."""

        return self.devices[name]

    def add_device(self, name, channel=None, device_class=None, **kwargs):
        """Adds a device

        Parameters
        ----------
        name : str or .Device
            The name of the device. It is treated as case-insensitive. It can
            also be a `.Device` instance, in which case the remaining
            parameters will be ignored.
        channel : int
            The channel of the device in the module (relative to the
            module address), zero-indexed.
        device_class : class
            Either `.Device` or a subclass of it.
        kwargs : dict
            Other parameters to pass to `.Device`.

        """

        if isinstance(name, Device):

            device = name

        else:

            device_class = device_class or Device

            if name in self.devices:
                raise DriftError(f'Device {name!r} already exists in '
                                 f'module {self.name!r}.')

            device = device_class(self, name, channel, **kwargs)

        self.devices[device.name] = device
        log.info(f'Added device {device.name} to module {self.name}.')

        return device

    def remove_device(self, name):
        """Removes a device.

        Parameters
        ----------
        name : str
            The name of the device to remove.

        """

        device = self.devices.pop(name)
        log.info(f'Removed device {name} from module {self.name}.')

        return device


class Device(object):
    """A device connected to a modbus `.Module`.

    Parameters
    ----------
    module : .Module
        The `.Module` to which this device is connected to.
    name : str
        The name of the device. It is treated as case-insensitive.
    channel : int
        The channel of the PLC inside the module, zero-indexed, so that the
        first channel is 0 and the full address of the device is
        ``module_address + channel - 40001``.
    coils : bool
        Whether to read coils or registers for this device.
    category : str
        A user-defined category for this device. This can be used to group
        different devices of similar type, for example ``'temperature'`` to
        indicate temperature sensors.
    description : str
        A description of the purpose of the device.
    units : str
        The units of the values returned, if an adaptor is used.
    adaptor : str, dict, or function
        The adaptor to be used to convert read registers to physical values.
        It can be a string indicating one of the provided :ref:`adaptors
        <adaptors>`, a string with the format ``module1.module2:function``
        (in this case ``module1.module2`` will be imported and ``function``
        will be called), a function or lambda function, or a mapping of
        register value to return value. If the adaptor is a function it must
        accept a raw value from the register and return the physical value,
        or a tuple of ``(value, unit)``.

    """

    __type__ = None

    def __init__(self, module, name, channel, coils=False, description='',
                 units=None, category=None, adaptor=None):

        assert isinstance(module, Module), 'module not a valid Module object.'

        self.module = module
        self.name = name
        self.channel = channel
        self.coils = coils
        self.description = description
        self.units = units
        self.category = category
        self.adaptor = self._parse_adaptor(adaptor)

        log.info(f'Created device '
                 f'{self.name}@{self.module.address}:{self.channel}.')

    def __repr__(self):
        return (f'<Device {self.name}@{self.module.address}:{self.channel}>')

    def _parse_adaptor(self, adaptor):
        """Parses the adaptor."""

        if adaptor is None:
            return None

        elif isinstance(adaptor, str):

            if ':' in adaptor:
                try:
                    module_str, adaptor = adaptor.split(':')
                except ValueError:
                    raise DriftError(f'Badly formatted adaptor {adaptor}.')
                module = importlib.import_module(module_str)
            else:
                module = adaptors

            if hasattr(module, adaptor) is False:
                raise DriftError(f'Cannot find adaptor {adaptor}.')
            else:
                return getattr(module, adaptor)

        elif isinstance(adaptor, (tuple, list, dict)):
            return dict(adaptor)

    @property
    def address(self):
        """Returns the full address of this PLC."""

        return self.module.address + self.channel - 40001

    @property
    def client(self):
        """Returns the ``pymodbus`` client."""

        return self.module.drift.client

    async def read(self, adapt=True):
        """Reads the value of the coil or register.

        If ``adapt=True`` and a valid adaptor was provided, the value returned
        is the one obtained after applying the conversion function to the
        raw register value. Otherwise returns the raw value.

        Returns
        -------
        read_value : tuple
            A tuple in which the first element is the read raw or converted
            value and the second is the associated unit. If ``adapt=False`` no
            units are returned.

        """

        async with self.module.drift:

            protocol = self.client.protocol

            if self.coils:
                reader = protocol.read_coils
            else:
                reader = protocol.read_input_registers

            resp = await reader(self.address, count=1)

            if resp.function_code > 0x80:
                raise DriftError(f'Invalid response for device '
                                 f'{self.name!r}: 0x{resp.function_code:02X}.')

            value = resp.registers[0] if not self.coils else resp.bits[0]

            if not adapt:
                return value

            if adapt and self.adaptor is not None:
                if callable(self.adaptor):
                    value = self.adaptor(value)
                else:
                    if value not in self.adaptor:
                        raise DriftError(f'Cannot find associated value for '
                                         f'{value} in adaptor mapping.')
                    else:
                        value = self.adaptor[value]

            if isinstance(value, (tuple, list)):
                value, units = value
            else:
                units = self.units

        return value, units

    async def write(self, value):
        """Writes values to a coil or register."""

        if self.module.mode != 'output':
            raise DriftError('Writing is not allowed to this module.')

        async with self.module.drift:

            protocol = self.client.protocol

            if self.coils:
                resp = await protocol.write_coil(self.address, value)
            else:
                resp = await protocol.write_register(self.address, value)

            if resp.function_code > 0x80:
                raise DriftError(f'Invalid response for device {self.name!r}: '
                                 f'0x{resp.function_code:02X}.')

        return True


class Relay(Device):
    """A device representing a relay.

    The main difference with a normal `.Device` is that the adaptor is defined
    by the ``relay_type``, which can be normally closed (NC) or normally open
    (NO).

    """

    __type__ = 'relay'

    def __init__(self, *args, relay_type='NC', **kwargs):

        self.relay_type = relay_type

        if relay_type == 'NC':
            adaptor = [(False, 'closed'), (True, 'open')]
        else:
            adaptor = [(False, 'open'), (True, 'closed')]

        kwargs['adaptor'] = adaptor

        if 'coils' not in kwargs:
            kwargs['coils'] = True

        super().__init__(*args, **kwargs)

    async def open(self):
        """Opens the relay."""

        if self.relay_type == 'NC':
            await self.write(True)
        else:
            await self.write(False)

    async def close(self):
        """Closes the relay."""

        if self.relay_type == 'NC':
            await self.write(False)
        else:
            await self.write(True)

    async def switch(self):
        """Switches the state of the relay."""

        await self.write(not await self.read(adapt=False))

    async def cycle(self, delay=1):
        """Cycles a relay, waiting ``delay`` seconds."""

        await self.switch()
        await asyncio.sleep(delay)
        await self.switch()


class Drift(object):
    """Interface to the modbus network.

    Parameters
    ----------
    address : str
        The IP of the TCP modbus server.
    port : int
        The port of the TCP modbus server.
    loop
        The event loop to use.


    The `.Drift` manages the TCP connection to the modbus ethernet module
    using `Pymodbus <pymodbus.readthedocs.io/en/latest/index.html>`__. The
    :class:`~pymodbus.client.asynchronous.async_io.AsyncioModbusTcpClient`
    object can be accessed as ``Drift.client``.

    In general the connection is opened and closed using the a context
    manager ::

        drift = Drift('localhost')
        async with drift:
            coil = drift.client.protocol.read_coils(40001, count=1)

    This is not needed when using `.Device.read` or `.Device.write`, which
    handle the connection to the server.

    """

    def __init__(self, address, port=502, loop=None):

        self.address = address
        self.port = port
        self.client = AsyncioModbusTcpClient(address, port=port, loop=loop)
        self.loop = self.client.loop

        self.modules = CaseInsensitiveDict()

    def __repr__(self):
        return f'<Drift @ {self.address}>'

    async def __aenter__(self):
        """Initialises the connection to the server."""

        try:
            await asyncio.wait_for(self.client.connect(), timeout=1)
        except asyncio.TimeoutError:
            raise DriftError(f'Failed connecting to server at {self.address}.')

        if not self.client.connected:
            raise DriftError(f'Failed connecting to server at {self.address}.')

        log.debug(f'Connected to {self.address}.')

        return

    async def __aexit__(self, exc_type, exc, tb):
        """Closes the connection to the server."""

        self.client.stop()

        log.debug(f'Disonnected from {self.address}.')

        return

    def __getitem__(self, name):
        """Gets a module."""

        return self.modules[name]

    def add_module(self, name, address, **params):
        """Adds a new module.

        Parameters
        ----------
        name : str
            The name of the module.
        address : int
            The modbus address.
        params : dict
            Arguments to be passed to `.Module` for initialisation.

        """

        if name in self.modules:
            raise ValueError(f'Module {name} is already connected.')

        self.modules[name] = Module(name, self, address, **params)

        return self.modules[name]

    def get_device(self, device):
        """Gets the `.Module` instance that matches ``device``.

        If the case-insensitive name of the device is unique within the pool
        of connected devices, the device name is sufficient. Otherwise the
        device must be provided as ``module.device``.


        """

        if '.' in device:
            module, device = device.split('.')
            return self.modules[module].devices[device]

        device = device.lower()

        dev_to_mod = defaultdict(list)
        for module in self.modules:
            for dev in self.modules[module].devices:
                dev_to_mod[dev.lower()].append(module.lower())

        if device not in dev_to_mod:
            raise ValueError(f'Device {device} is not connected.')

        elif len(dev_to_mod[device]) == 1:
            return self.modules[dev_to_mod[device.lower()][0]].devices[device]

        else:
            raise ValueError(f'Multiple devices with name {device} found. '
                             'Use a module-qualified name.')

    async def read_device(self, name, adapt=True):
        """Reads a device.

        Parameters
        ----------
        adapt : bool
            If possible, convert the value to real units.

        Returns
        -------
        read_value : tuple
            The read value and its associated units.

        """

        return await self.get_device(name).read(adapt=adapt)

    async def read(self, *args, **kwargs):
        """Alias for `.read_device`."""

        return await self.read_device(*args, **kwargs)

    async def read_category(self, category, adapt=True):
        """Reads all the devices of a given category.

        Parameters
        ----------
        category : str
            The category to match.
        adapt : bool
            If possible, convert the value to real units.

        Returns
        -------
        read_values : dict
            A dictionary of module-qualified device names and read values,
            along with their units.

        """

        values = {}

        for module in self.modules:
            for device in self.modules[module].devices.values():
                name = f'{module}.{device.name.lower()}'
                if device.category and device.category.lower() == category:
                    values[name] = await device.read(adapt=adapt)

        return values

    @classmethod
    def from_config(cls, config):
        """Loads a Drift from a dictionary or YAML file.

        Parameters
        ----------
        config : dict or str
            A properly formatted configuration dictionary or the path to a
            YAML file from which it can be read. Refer to :ref:`config-file`
            for details on the format.

        """

        if isinstance(config, str):
            config = load(open(config, 'r'), Loader=SafeLoader)

        address = config['address']
        port = config.get('port', 502)

        new_drift = cls(address, port)

        for module in config.get('modules', {}):

            module_config = config['modules'][module]
            devices = module_config.pop('devices', {})

            new_drift.add_module(module, **module_config)

            for device in devices:

                device_config = devices[device].copy()
                channel = device_config.pop('channel')
                device_class = None
                type_ = device_config.pop('type', None)

                if type_:
                    for subclass in Device.__subclasses__():
                        if subclass.__type__ == type_:
                            device_class = subclass
                            break
                else:
                    device_class = Device

                if device_class is None:
                    raise DriftError('Cannot find valid device class for '
                                     f'type {type_}.')

                new_drift.modules[module].add_device(device, channel,
                                                     device_class,
                                                     **device_config)

        return new_drift
