# Changelog


## 0.2.2 - May 18, 2021

### 🔧 Fixed

* Fix a nasty bug that would force all relays to be of mode `coil` even if its module has been defined as a `holding_register`. Also, fix the writing of bits when `channel` is set in a holding register.


## 0.2.1 - February 23, 2021

### 🔧 Fixed

* Add a lock to the connection context manager to prevent multiple simultaneous connections disconnecting the client.


## 0.2.0 - February 22, 2021

### 🚀 New

* Major rewrite of how addresses, channels, and modes work.
* Rename E+E adaptors and add `rtd10` adaptor.
* Add `voltage`, `pwd`, `flow`, and `linear` adaptors.

### 🔧 Cleanup

* [#4](https://github.com/sdss/drift/issues/4) Add typing and use Black formatting.


## 0.1.5 - October 10, 2020

### 🔧 Fixed

* [#3](https://github.com/sdss/drift/issues/3) Fix import of `AsyncioModbusTcpClient` when using `pymodbus>=2.4.0`.


## 0.1.4 - August 19, 2020

### 🔧 Cleanup

* Do not require extra `dev` for `sdsstools`.


## 0.1.3 July 30, 2020

### 🚀 New

* Add `Drift.read` alias to `Drift.read_device`.

### 🔧 Fixed

* Fix `Drift.get_device` not working for case-insensitive devices.


## 0.1.2 - July 29, 20202

### 🔧 Cleanup

* Relax `sdsstools` version to allow `jaeger` to bump the minimum version.


## 0.1.1 - July 19, 2020

### 🔧 Cleanup

* Updated release workflow.
* Expose exceptions.


## 0.1.0 - July 19, 2020

### 🚀 New

* Initial version, based on `jaeger`'s code.
* Added testing suite.
* Added documentation.
