..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================
Support Placement API
=====================

https://blueprints.launchpad.net/watcher/+spec/support-placement-api


Problem description
===================

Placement provides a service for managing, selecting, and claiming
available resources in a cloud. It was introduced in the Newton release
within the nova repository and extracted to the placement repository
in the Stein release.
Now Watcher gets data directly from Nova for building data model
and strategies processing. But some data, such as overcommit allocation
ratio for VCPU and Ram, can't get from Nova. The knowledge available
to strategies to make informed decisions is currently limited due to
the placement api being unavailable.

Use Cases
----------

As a Watcher developer, I want to get data from Placement.


Proposed change
===============

In this spec we just add Placement helper to Watcher.
We plan to improve the data model and strategies in
the future specs.
The functions in the helper as below:

* List resource providers
* List resource classes
* List resource provider inventories
* List resource provider traits
* List resource provider allocations
* List resource provider usages
* List allocation candidates

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

None

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

Add a new config section [placement_client].

Some config options:

* api_version: The minimum version restricted to a given Major API.
* interface: The default interface for URL discovery.
* region_name: The default region_name for URL discovery.

Developer impact
----------------

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  licanwei

Work Items
----------

* Add Placement helper
* Add unit test


Dependencies
============

None


Testing
=======

Unittest for Placement helper


Documentation Impact
====================

None


References
==========

https://developer.openstack.org/api-ref/placement/


History
=======


.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Train
     - Introduced

