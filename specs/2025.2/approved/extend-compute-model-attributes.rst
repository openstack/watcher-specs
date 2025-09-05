..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===============================
Extend Compute Model Attributes
===============================

https://blueprints.launchpad.net/watcher/+spec/extend-compute-model-attributes


Problem description
===================

When creating a solution to achieve a goal, Watcher commonly builds an action
plan composed of multiple actions, which are mostly based on Server
Migrations. These computed migrations are not always valid from Nova's point
of view since they can violate some placement constraints defined for a
server, which Watcher is not aware of. Watcher could be improved to include
additional constraints and other compute resources in its models, to assist
strategies on building action plans. This blueprint proposes extending
Watcher's compute model to include additional compute attributes.

Use Cases
----------

As an OpenStack Admin I would like to optimize my deployment, balancing the
workload across compute nodes, without breaking any placement constraints
associated with its instances like: flavor extra specs, affinity and
anti-affinity policies, pinned availability zones, etc.

Proposed change
===============

This blueprint proposes to extend the current compute model to include
additional instance's attributes, available in the new API versions of
``GET /servers/detail`` API:

* Pinned Availability Zone: defines that an instance should be pinned to an
  availability zone and this parameter should also be considered when
  migrating it.
* Flavor Extra Specs: specs that can include hardware requirements, resource
  allocation policies, and custom placement rules that influence how servers
  are scheduled across the infrastructure.

.. note::
   If the configured compute API microversion is lower than the required
   ones, these new attributes will be left as empty, and strategies will
   not take the advantage of this proposed extension.

.. note::
   The amount of new attributes is limited by Wacther's maximum supported
   compute API microversion. Since Watcher's Nova Collector implementation
   is based on the usage of the ``python-novaclient``
   library, the maximum supported compute API microversion is limited to
   the same as the one supported by the library (which is the 2.96 for
   now). This limitation can be overcome by changing the implementation
   to use the ``openstacksdk`` library instead, but this is not in the scope
   of this specification.

A new configuration option will be added to the collector, to allow Admin to
enable or disable the collection of these additional attributes. It will be
set to disable by default, but can be changed in the next cycles once
Strategies start to consume its content.

The API microversion will increased in favor of the new attributes to be
added in the response body of `GET /v1/data_model` call.

Alternatives
------------

In order to improve the host selection, Watcher could rely on Nova to provide
the list of valid destination hosts for a server migration. However, this API
does not exist in Nova and implementing it can also be a challenge, since
Nova's Scheduler is not ready to answer to these requests, without reserving
the resources associated with them. This alternative would also increase the
amount of API requests to Nova, since some strategies calculates multiple
solutions before selecting the best one.

Data model impact
-----------------

New fields will be added to the `Instance Element` class, which is an
element of the Nova Cluster Data Model. The new fields are the
following::

  "server_pinned_az": wfields.StringField(),
  "flavor_extra_specs": wfields.JsonField(),

REST API impact
---------------

A new API microversion will introduce new attributes to the
response body of the `GET /v1/data_model` method.
Example of the new attributes in the response json:

  .. code-block::


      {
          "server_pinned_az": "us-west",
          "server_flavor_extra_specs": {
            "hw:watchdog_action": "reset",
          },
          ....

Security impact
---------------

None.

Notifications impact
--------------------

None.

Other end user impact
---------------------

None.

Performance Impact
------------------

* A minimal impact is expected since the in-memory model will be extended
  and have more fields. A configuration option will allow users to disable
  extended Instance fields, reducing the impact to almost zero.

Other deployer impact
---------------------

None.

Developer impact
----------------

When developing a new Strategy or updating an existing one, developers can
consider these new constraints when selecting a destination host for a server
migration.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  dviroel

Work Items
----------

* Extend Nova Cluster Data Model to include new Instance attributes.
* Update the Nova Collector to parse additional Instance attributes.
* Extend Nova Notifications processing to update new attributes.

Dependencies
============

Some attributes are only available in newer versions of Nova's API:

  * Flavor Extra Specs: microversion 2.47 (already supported)
  * Pinned Availability Zone: microversion 2.96

To achieve better results, it is expected that deployed Nova supports
most of the above microversions.

Testing
=======

Unit tests will cover different scenarios when collecting data from
Nova service.
A new tempest test will create instances with additional attributes and
validate that this info is available in the new model.
A devstack job will be modified to enable the additional attributes
collection and run new tempest tests.

Documentation Impact
====================

Update documentation that mention model collectors, to include
information about additional attributes in newer microversions.

References
==========

None.

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - 2025.2
     - Introduced
