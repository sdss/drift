
SDSS-V `Drift <https://pacificrim.fandom.com/wiki/Drift>`__'s documentation
===========================================================================

This is the documentation for the SDSS-V product `drift <https://github.com/sdss/drift>`__. The current version is |drift_version|. See :ref:`what's new <drift-changelog>`.


.. toctree::
    :hidden:

    CHANGELOG


Overview
--------

This library provides an asynchronous interface with modbus devices over a TCP ethernet controller (such as `this one <https://www.drift.com/us/controllers-bus-couplers-i-o/controller-modbus-tcp/p/750-862>`__) and control of the connected I/O modules. The code is a relatively thin wrapper around `Pymodbus <http://riptideio.github.io/pymodbus/>`__ with the main feature being that it's possible to define a PLC controller and a complete set of modules as a YAML configuration file which can then be loaded. It also provides convenience methods to read and write to the I/O modules and to convert the read values to physical units.

This code is mostly intended to interface with the SDSS-V `FPS <https://www.sdss.org/future/technology/>`__ electronic boxes but is probably general enough for other uses. It's originally based on Rick Pogge's `WAGO code <https://github.com/sdss/FPS/tree/master/WAGO>`__.


Installation
------------

To install, run

.. code-block:: sh

    pip install sdss-drift

To install from source, git clone or download the code, navigate to the root of the downloaded directory, and do

.. code-block:: sh

    pip install .

``sdss-drift`` uses `Poetry <https://poetry.eustace.io/>`__ for development. To install it in development mode do

.. code-block:: sh

    poetry install -E docs


Basic use
---------

Let's start with a basic example ::

    >>> from drift import Drift

    >>> drift = Drift('10.1.10.1')
    >>> module1 = drift.add_module('module1', 40010, channels=4, mode='input')
    >>> sensor1 = module1.add_device('sensor1', 0, adaptor='ee_temp', description='Temperature sensor')

    >>> await sensor1.read()
    (25.0, 'degC')

Here `.Drift` handles the connection to the modbus ethernet interface. `Modules <.Module>` represent physical analog or digital I/O components connected to the modbus network. We added a single analog input module with starting modbus address 40010 (note that in modbus addresses start with 40001) and four channels. Finally, we add a single `.Device` to the module, a temperature sensor connected to the first channel (zero-indexed).

``drift`` is an asynchronous library that uses the Python standard library `asyncio`. Procedures that read or write from the modbus network are defined as coroutines so that the process can be handled asynchronously. This is shown in the fact that we need to *await* the call to `sensor1.read() <.Device.read>`.

It's also possible to define a module by providing a product serial number ::

    >>> drift.add_module('module2', 40101, model='750-530')
    >>> drift['module2'].mode
    'output'
    >>> drift['module2'].channels
    8

By providing the serial number of the `WAGO 750-530 <https://www.wago.com/us/controllers-bus-couplers-i-o/8-channel-digital-output/p/750-530>`__ digital output we don't need to provide the mode or number of channels. We still need to provide the initial address for which the module is configured.

Let's now add a relay to channel 4 ::

    >>> drift['module2'].add_device('relay1', 3 coils=True)
    >>> relay = drift.get_device('relay1')
    >>> await relay.read()
    (True, None)
    >>> await relay.write(False)
    >>> await relay.read()
    (False, None)

Note that we create this device with ``coils=True`` since we'll be reading from and writing to a binary coil instead of a register. We can also use `.get_device` to retrieve a device. Module and device names are considered case-insensitive. If the name of the device is not unique, the module-qualified name (e.g., ``'module1.relay1'``) must be used.


.. _adaptors:

Adaptors
--------

In our first example we created a new device with ``adaptor='ee_temp'``. Adaptors are simply functions that receive a raw value from a register or coil and return a tuple with the physical value and, optionally, the associated units. When `~.Device.read` is awaited, the adaptor (if it has been defined) will be called with the raw value and the result returned ::

    >>> await sensor1.read()
    (25.0, 'degC')

This can be disabled by using ``adapt=False`` ::

    >>> await sensor1.read(adapt=False)
    18021

Adaptors can be defined as a function or lambda function ::

    >>> module.add_device('device', 0, adaptor=lambda raw_value: (2 * raw_value, 'K'))

A number of adaptors are provided with ``drift``, see :ref:`available-adaptors`. The name of one of these adaptor functions, as a string, can be used. It's possible to define an adaptor in the form ``module1.module2:my_adaptor``. In this case ``from module1.module2 import my_adaptor`` will be executed and ``my_adaptor`` used.

Finally, one can define an adaptor using a mapping of raw value to converted value, as a dictionary or tuple, for example ``[(1, 2), (4, 8)]`` will convert raw_value 1 into 2, and 4 into 8. If a raw value not contained in the mapping is read, an error will be raised.


Relays
------

`.Device` can be subclassed to provide a better API for specific kinds of device. A typical case of device is a relay, which can be normally open (NO) or normally closed (NC). ``drift`` provides a `.Relay` class that simplifies the handling of a relay ::

    >>> from drift import Relay
    >>> module.add_device(
        'relay_no', 3, device_class=Relay, relay_type='NO',
        description='A normally open relay'
    )

Now we can read the state of the relay ::

    >>> relay = drift.get_device('relay_no')
    >>> await relay.read()
    ('open', None)

Note that this would be equivalent to creating a normal `.Device` with an adaptor such as ``[(False, 'open'), (True, 'closed')]``.

`.Relay` comes with a number of convenience functions to `.open`, `.close`, `.switch`, or `.cycle` a relay ::

    >>> await relay.read()
    ('open', None)
    >>> await relay.close()
    >>> await relay.read()
    ('closed', None)
    >>> await relay.switch()
    >>> await relay.read()
    ('open', None)


.. _config-file:

Configuration file
------------------

Programmatically defining the modules and devices in an electronic design can become tiresome once we have more than a bunch of elements. In those cases, we can define the components in a YAML configuration file, for example

.. code-block:: yaml

    # file: sextant.yaml

    address: 10.1.10.1
    port: 502
    modules:
        module_rtd:
            model: "750-450"
            mode: input
            channels: 4
            address: 40009
            description: "Pt RTD sensors"
            devices:
                "RTD1":
                    channel: 0
                    category: temperature
                    adaptor: rtd
                    units: degC
                "RTD2":
                    channel: 1
                    category: temperature
                    adaptor: rtd
                    units: degC
        module_do:
            model: "750-530"
            mode: output
            channels: 8
            address: 40513
            description: "Power relays"
            devices:
                "24V":
                    channel: 0
                    type: relay
                    relay_type: NC
                "5V":
                    channel: 1
                    type: relay
                    relay_type: "NO"

Most parameters match the arguments of `.Drift`, `.Module`, and `.Device`. Note that for the two relays we indicate that ``type: relay`` which will result in using the `.Relay` class instead of the generic `.Device`.

To create a new `.Drift` instance based on this configuration we do ::

    >>> drift = Drift.from_config('sextant.yaml')
    >>> len(drift.modules)
    2
    >>> len(drift['module_do'].devices)
    2
    >>> await drift.get_device('24v').read()
    ('closed', None)


API
---

.. autoclass:: drift.drift.Drift
    :members:

.. autoclass:: drift.drift.Module
    :members:

.. autoclass:: drift.drift.Device
    :members:

.. autoclass:: drift.drift.Relay
    :members:

.. _available-adaptors:

Available adaptors
^^^^^^^^^^^^^^^^^^

.. automodule:: drift.adaptors
    :members:
