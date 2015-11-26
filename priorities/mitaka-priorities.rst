.. _mitaka-priorities:

=========================
Mitaka Project Priorities
=========================

List of priorities (in the form of use cases) the Watcher development team is prioritizing in Mitaka.
This is still very much a work-in-progress.

+---------------------------+-----------------------+
| Priority                  | Owner                 |
+===========================+=======================+
| `DevStack integration`_   | `Taylor Peoples`_     |
| `Ceilometer integration`_ | `Jean-Emile Dartois`_ |
| `Dynamic strategy load`_  | `Vincent Francoise`_  |
| `Tempest integration`_    | `David Tardivel`_     |
+---------------------------+-----------------------+


.. _Taylor Peoples: https://launchpad.net/~tpeoples
.. _Jean-Emile Dartois: https://launchpad.net/~jed56
.. _Vincent Francoise: https://launchpad.net/~vincent-francoise
.. _David Tardivel: https://launchpad.net/~david-tardivel


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

Watcher must be able to load different optimization strategies.

Tempest integration
-------------------

Watcher must provide a set of integration tests that will be used by
Tempest.