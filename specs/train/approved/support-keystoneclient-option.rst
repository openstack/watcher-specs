..
   This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=============================
Support keystoneclient option
=============================

https://blueprints.launchpad.net/watcher/+spec/support-keystoneclient-option


Currently, users can modify the default parameters through the configuration
file when creating novaclient and cinderclient, but it is not allowed when
creating keystoneclient.


Problem description
===================

The type of endpoint and region name can not be set when creating
keystoneclient. Users may want to modify these parameters in different
demand scenarios.

Use Cases
----------

As a user of Watcher, I want to specify the type of endpoint and region name
when creating keystoneclient by the configuration file.

As a user of Watcher, I want to specify the type of endpoint as internal
when creating keystoneclient by the configuration file.

As a user of Watcher, I want to specify the value of region name as RegionTwo
when creating keystoneclient by the configuration file.


Proposed change
===============

Allow specifying the type of endpoint and region name when creating
keystoneclient by exposing new configuration parameter. These parameters
will be part of a new group labeled keystone_client.

::

    [keystone_client]
    interface = internal
    region_name = RegionOne

The interface will default to admin since that is what is used today:

https://github.com/openstack/python-keystoneclient/blob/3.15.0/keystoneclient/httpclient.py#L251

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

None

Developer impact
----------------

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <chenker>

Work Items
----------

* Add the definition and register of keystone_client group.

* Add the definition and register of keystone_client option.

* Update the default access method of keystone_client option.


Dependencies
============

None

Testing
=======

* Determine if keystone_client option is used correctly.


Documentation Impact
====================

Documentation on configuration parameters will need to be updated to reflect
the new parameters.


References
==========

https://review.opendev.org/#/c/658102/


History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Train
     - Introduced
