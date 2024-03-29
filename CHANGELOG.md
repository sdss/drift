# Changelog

## 1.1.0 - September 12, 2023

### 🚀 New

* Allow to set the connection timeout when initialising `Drift`.

### ⚙️ Engineering

* Lint with `ruff`.
* Update codebase to work with `pymodbus` 3.5+.


## 1.0.2 - March 10, 2023

### 🔧 Fixed

* Pin `pymodbus<3.2.0`. This versions removes the `protocol` attribute in `AsyncioModbusTcpClient` and breaks `drift`. It will be fixed in a future version.


## 1.0.1 - December 24, 2022

### 🔧 Fixed

* Fixed reconnection. `pymodbus` now set the host to `None` after the transport closes, so it needs to be rested before reconnecting.


## 1.0.0 - December 24, 2022

### 🚀 New

* Dropped Python 3.7 and add support for 3.11 with `pymodbus>=3.0.0`.


## 0.4.5 - November 9, 2022

### 🔧 Fixed

* Release lock if connection fail in `Drift.__aenter__`.


## 0.4.4 - May 25, 2022

### 🚀 New

* `Drift()` can now be initialised with `lock=False` which will disable the locking of the client while the context manager is used. In this mode, multiple concurrent connections to the client are allowed.
* Added `Drift.read_devices()` which allows reading multiple devices concurrently with only one connection to the client.
* `Drift.devices` returns a list of all connected devices.

### ✨ Improved

* `Module` does not require to pass a number of channels anymore. In fact the number of channels is never used so it may be deprecated in the future.
* Add poetry dependency groups.


## 0.4.3 - May 13, 2022

### 🎨 Engineering

* Use latest pre-release version of poetry core, do not require `setuptools`, and test for 3.10.


## 0.4.2 - May 11, 2022

### ✨ Improved

* `Drift.from_config()` now accepts keyword arguments that are passed to `__init__()`.


## 0.4.1 - February 4, 2022

### 🚀 New

* [#9](https://github.com/sdss/drift/issues/9) `Device` now accepts a `data_type` argument that follows the same format as the [struct](https://docs.python.org/3/library/struct.html#format-characters) module and allows to cast the read raw value from unsigned 16-bit integer to a different type, before passing it to an adaptor.


## 0.4.0 - December 14, 2021

### 💥 Breaking changes

* Device addresses now must include the offset (i.e., 40001 is not subtracted).

### 🚀 New

* Add proportional adaptor.


## 0.3.0 - October 12, 2021

### 🚀 New

* Add the option to add an offset to the read value after applying the adaptor.

### ✨ Improved

* Updated documentation theme to ``furo``.

### 🔧 Fixed

* Fix case when linear adaptor range does not start at zero.


## 0.2.5 - August 1, 2021

### ✨ Improved

* Added `gain` parameter to `voltage` adaptor.


## 0.2.4 - July 27, 2021

### 🔧 Fixed

* [#7](https://github.com/sdss/drift/issues/7) If the connection to the client fails, release the lock immediately.


## 0.2.3 - July 15, 2021

### 🔧 Fixed

* [#5](https://github.com/sdss/drift/issues/5) Fixed an error that would happen when switching the first (channel 0) bit in a holding register. In that case the code would just set the entire register, ignoring the other set bits.


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
