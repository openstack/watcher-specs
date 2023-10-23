..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

============
MAAS support
============

https://blueprints.launchpad.net/watcher/+spec/maas-support

This blueprint aims to introduce Watcher support for MAAS, another bare metal
provisioning and management service that's commonly used with Openstack.

Problem description
===================

Metal-As-A-Service (MAAS) is an open source project led by Canonical that
allows provisioning and managing bare metal nodes.

Right now, Watcher can only use Ironic, however MAAS support can be added with
minimal changes.

Use Cases
----------

Some Openstack clusters are deployed using MAAS + Juju instead of Ironic.
By adding MAAS support, we'll allow Watcher to discover MAAS nodes and perform
power actions, adjusting the number of running nodes based on the current
workload.

Proposed change
===============

We'll add a simple bare metal client abstraction with concrete implementations
for Ironic and MAAS.

If a MAAS endpoint and credentials are provided, we'll pick the MAAS client,
otherwise defaulting to the Ironic client.

The python-libmaas client will be used to interact with the MAAS service.

Alternatives
------------

None

Data model impact
-----------------

None

REST API impact
---------------

None

Security impact
---------------

A MAAS authentication key will have to be provided through a config option.

Notifications impact
--------------------

None

Other end user impact
---------------------

None

Performance Impact
------------------

None

Other deployer impact
---------------------

The MAAS URL and authentication key will have to be configured when using
MAAS.

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <petrutlucian94>

Work Items
----------

* Add new Watcher config options
* Add metal client abstraction
* Provide proper test coverage
* Update Juju Watcher charm, exposing the new config options

Dependencies
============

None

Testing
=======

Unit tests will be provided for the newly added code.

Power cycle operations are disruptive and can affect other tests, which
is probably the reason why there are no existing functional or integration
tests for the "energy saving" strategy. Such tests would excercise the MAAS
client as well.

Documentation Impact
====================

The new MAAS related config options will have to be documented. Also, some
Ironic references may need to be updated, reflecting the fact that Watcher
can now use more than one bare metal management service.

References
==========

* https://maas.io
* https://git.launchpad.net/maas/
* https://github.com/maas/python-libmaas
* https://github.com/openstack/charm-watcher

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Caracal
     - Introduced

