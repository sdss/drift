# SDSS-V Modbus PCL library

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Documentation Status](https://readthedocs.org/projects/sdss-drift/badge/?version=latest)](https://sdss-drift.readthedocs.io/en/latest/?badge=latest)
![Build](https://img.shields.io/github/workflow/status/sdss/drift/Test)
[![codecov](https://codecov.io/gh/sdss/drift/branch/master/graph/badge.svg)](https://codecov.io/gh/sdss/drift)

This library provides an asynchronous interface with modbus devices over a TCP ethernet controller (such as [this one](https://www.wago.com/us/controllers-bus-couplers-i-o/controller-modbus-tcp/p/750-862)) and control of the connected I/O modules. The code is a relatively thin wrapper around [Pymodbus](http://riptideio.github.io/pymodbus/) with the main feature being that it's possible to define a PLC controller and a complete set of modules as a YAML configuration file which can then be loaded. It also provides convenience methods to read and write to the I/O modules and to convert the read values to physical units.

This code is mostly intended to interface with the SDSS-V [FPS](https://www.sdss.org/future/technology/) electronic boxes but is probably general enough for other uses. It's originally based on Rick Pogge's [WAGO code](https://github.com/sdss/FPS/tree/master/WAGO).

## Installation

To install, run

```console
pip install sdss-drift
```

To install from source, git clone or download the code, navigate to the root of the downloaded directory, and do

```console
pip install .
```

`sdss-drift` uses [Poetry](https://poetry.eustace.io/) for development. To install it in development mode do

```console
poetry install -E docs
```

## Documentation

Refer to the Read the Docs [documentation](https://sdss-drift.readthedocs.io/en/latest) for more details.
