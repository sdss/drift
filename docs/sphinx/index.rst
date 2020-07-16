
SDSS-V WAGO's documentation
===========================

This is the documentation for the SDSS-V product `WAGO <https://github.com/sdss/WAGO>`__. The current version is |wago_version|. See :ref:`what's new <wago-changelog>`.


Overview
--------

This library provides an interface with the WAGO ethernet controller (such as `this one <https://www.wago.com/us/controllers-bus-couplers-i-o/controller-modbus-tcp/p/750-862>`__) and control of the connected I/O modules. The code is a relatively thin wrapper around `Pymodbus <http://riptideio.github.io/pymodbus/>`__ with the main feature being that it's possible to define a PLC controller and a complete set of modules as a YAML configuration file which can then be loaded. It also provides convenience methods to read and write to the I/O modules and to convert the read values to physical units.

This code is mostly intended to interface with the SDSS-V `FPS <https://www.sdss.org/future/technology/>`__ electronic boxes but it's probably general enough for other uses. It's originally based on Rick Pogge's `WAGO code <https://github.com/sdss/FPS/tree/master/WAGO>`__.


Installation
------------

To install, run

.. code-block:: sh

    pip install sdss-wago

To install from source, git clone or download the code, navigate to the root of the downloaded directory, and do

.. code-block:: sh

    pip install .

``sdss-wago`` uses `Poetry <https://poetry.eustace.io/>`__ for development. To install it in development mode do

.. code-block:: sh

    poetry install -E docs
