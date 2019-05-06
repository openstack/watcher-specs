..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================================
Config global datasource preference
===================================

https://blueprints.launchpad.net/watcher/+spec/global-datasource-preference


Currently, datasources need to be configured on a per strategy basis.
Configuring the datasources per strategy is error prone and time consuming. By
being able to configure a global datasource preference the time to configure
Watcher is reduced and there is a single point for configuring the datasources
used by Watcher.


Problem description
===================

The datasources available to Watcher differs per OpenStack deployment so there
can not be a standard preference that will work for all deployments.
Configuring which datasources are preferred is essential to correctly deploying
Watcher, however, the datasource preference needs to be defined per strategy.
As a result the datasource preference will have to be configured many times
which can lead to errors and costs more time.

Use Cases
----------

As a user of Watcher, I want to configure the datasources only once.

As a user of Watcher, I want to configure the datasources only once but have
specific exceptions for some strategies.


Proposed change
===============

Allow specifying of global datasource order by exposing new configuration
parameter. This parameter will be part of a new group labeled
watcher_datasource. The datasource parameter for strategies remains available
and overrides the globally configured datasources.

::

    [watcher_datasource]
    datasources = ceilometer, gnocchi, monasca

Alternatives
------------

Try datasources but ensure that if they are not properly configured an error
is raised and an alternative datasource is tried. Major downside of this
approach is that it will create a lot of errors in some scenarios.

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
  <dantalion>

Work Items
----------

* Add configuration parameter to specify an order of preferred datasources.

* Read global datasource preference from config on selecting backend.

* Allow specific strategy datasource configurations to preference.

* On error attempt the next datasource.


Dependencies
============

None

Testing
=======

* Determine if global preference is used correctly.

* Determine if strategies can override the global preference.

Documentation Impact
====================

Documentation on configuration parameters will need to be updated to reflect
the new parameter.


References
==========

https://review.openstack.org/#/c/645294/


History
=======

None
