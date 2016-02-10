.. _mitaka-priorities:

=========================
Mitaka Project Priorities
=========================

List of priorities the Watcher drivers team is prioritizing in Mitaka.

+---------------------------+-----------------------+
| Priority                  | Owner                 |
+===========================+=======================+
| `DevStack integration`_   | `Taylor Peoples`_     |
+---------------------------+-----------------------+
| `Ceilometer integration`_ | `Jean-Emile Dartois`_ |
+---------------------------+-----------------------+
| `Dynamic strategy load`_  | `Jean-Emile Dartois`_ |
+---------------------------+-----------------------+
| `Tasflow integration`_    | `Jean-Emile Dartois`_ |
+---------------------------+-----------------------+
| `Tempest integration`_    | `Vincent Francoise`_  |
+---------------------------+-----------------------+
| `Scoring module`_         | `Tomasz Kaczynski`_   |
+---------------------------+-----------------------+
| `Cluster objects wrapper`_| `Taylor Peoples`_     |
+---------------------------+-----------------------+
| `Threshold optimization`_ | `Edwin Zhai`_         |
+---------------------------+-----------------------+
| `Watcher dashboard`_      | `David Tardivel`_     |
+---------------------------+-----------------------+

.. _Taylor Peoples: https://launchpad.net/~tpeoples
.. _Jean-Emile Dartois: https://launchpad.net/~jed56
.. _Vincent Francoise: https://launchpad.net/~vincent-francoise
.. _David Tardivel: https://launchpad.net/~david-tardivel
.. _Tomasz Kaczynski: https://launchpad.net/~tom-kaczynski
.. _Edwin Zhai: https://launchpad.net/~edwin-zhai


DevStack integration
--------------------

Watcher needs to be DevStack friendly such that it is easily approachable
for folks looking to use and/or contribute to Watcher.

Ceilometer integration
----------------------

Watcher must rely on Ceilometer to get metrics from the underlying
infrastructure.

Dynamic strategy load
---------------------

`Watcher Decision Engine`_ must be able to load different optimization
`Strategy`_ .

Tasflow integration
-------------------

`Watcher Applier`_ must use taskflow as it will help us a lot to make
`Action Plan`_ execution easy, consistent, scalable and reliable.

Tempest integration
-------------------

Watcher must provide a set of integration tests that will be used by
Tempest and run as a voting job in the gate.

Scoring module
--------------

Watcher scoring module is a generic machine learning service. It will provide
for example predictions or classifications that can be used by the selected
`Strategy`_.

Cluster objects wrapper
-----------------------

`Watcher Decision Engine`_  must provide a way to get cluster objects that can
be used directly within a `Strategy`_ . These objects will be refreshed
periodically.

Threshold optimization
----------------------

Watcher must allow the admin to pass `Strategy`_  parameters, like an
optimization threshold, to a selected `Strategy`_ .

Watcher dashboard
-----------------

Watcher must provide a human interface to interact through the OpenStack
Horizon dashboard.

.. _Strategy: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#strategy
.. _Watcher Decision Engine: https://factory.b-com.com/www/watcher/doc/watcher/architecture.html#watcher-decision-engine
.. _Action Plan: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action-plan
.. _Watcher Applier: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#watcher-applier

