.. _drift-changelog:

==========
Change Log
==========

* :bug:`-` Add a lock to the connection context manager to prevent multiple simultaneous connections disconnecting the client.

* :release:`0.2.0 <2021-02-22>`
* :support:`4` Add typing and use Black formatting.
* :feature:`-` Major rewrite of how addresses, channels, and modes work.
* :feature:`-` Rename E+E adaptors and add `.rtd10` adaptor.
* :feature:`-` Add `.voltage`, `.pwd`, `.flow`, and `.linear` adaptors.

* :release:`0.1.5 <2020-10-10>`
* :bug:`3` Fix import of ``AsyncioModbusTcpClient`` when using ``pymodbus>=2.4.0``.

* :release:`0.1.4 <2020-08-19>`
* :support:`-` Do not require extra ``dev`` for ``sdsstools``.

* :release:`0.1.3 <2020-07-30>`
* :feature:`-` Add `~.Drift.read` alias to `~.Drift.read_device`.
* :bug:`-` Fix `.Drift.get_device` not working for case-insensitive devices.

* :release:`0.1.2 <2020-07-29>`
* :support:`-` Relax ``sdsstools`` version to allow ``jaeger`` to bump the minimum version.

* :release:`0.1.1 <2020-07-19>`
* :support:`-` Updated release workflow.
* :support:`-` Expose exceptions.

* :release:`0.1.0 <2020-07-19>`
* :support:`-` Initial version, based on ``jaeger``'s code.
* :support:`-` Added testing suite.
* :support:`-` Added documentation.
