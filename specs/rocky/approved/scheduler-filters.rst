..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=================================
Respecting Nova Scheduler Filters
=================================

https://blueprints.launchpad.net/watcher/+spec/scheduler-filters

Problem description
===================

This specification continues ideas of `nova-policies`_ blueprint.
One of global business requirements to Watcher is a requirement to respect
Nova Scheduler filters at least in context of affinity/anti-affinity filters.
Many corporate customers build HA architecture for their cloud applications and
they want to respect virtual machine's policies, which are represented as
Nova Scheduler filters. There are the following typical filters which can be
used in the VMs booting process:
* To hold some VMs on `different`_ hosts (to achieve HA compatibility).
* To place VMs inside of specified host `aggregates`_ or `availability`_ zones.
* To place VMs only on enabled and `core-compatible`_ hosts.

As of now, Nova doesn't expose an open API to Nova Scheduler's
`select_destinations`_ method. This method is available for internal Nova's
usage and it isn't good architectural practice to access this method from a
third-party service like Watcher.

Use Cases
---------

As an openstack operator, I want to execute audit's with taking into account
Nova Scheduler filters.


Proposed change
===============

The main proposition is to add Watcher Filters pluggable system, that would
use set of Nova-compatible filters in auditing process. We can't import them
directly (cause OpenStack projects can import only project clients to interact
to each other), so we need to implement each filter in the way Nova does. Nova
Scheduler use internal objects ``host_state`` and ``spec_obj`` that represents
host and instance attributes respectively. We can replace these objects with
appropriate nodes from CDM. CDM consumes notifications via notification bus
system. Extending attributes in CDM nodes will depend on specific filter. If we
can consume notifications of changing availability zones or host aggregates,
we can add them to CDM as host attributes. Otherwise, we can get them by API
calls.

Primary logic should be saved to save compatibility with appropriate Nova's
filters. Let's take a look at Nova's DifferentHost filter:

::

    def host_passes(self, host_state, spec_obj):
        affinity_uuids = spec_obj.get_scheduler_hint('different_host')
        if affinity_uuids:
            overlap = utils.instance_uuids_overlap(host_state, affinity_uuids)
            return not overlap
        # With no different_host key
        return True

There should be created ``filter`` subfolder in decision_engine folder. It will
contain manager.py and filters/ folder with filter plugins. Filter Manager
will load enabled plugins and pass virtual machine along with destination host
through the list of the loaded plugins. Instance of FilterManager class should
be added to BaseStrategy class as class property to let each strategy filtering
VMs. Strategies should be reworked to get support for filters. Method
`self.verify_destination(instance, host)` can be added to BaseStrategy class
to simplify its usage for other strategies. There cannot be common point for
using filters in strategies because of unique workflow of each one.

In the current situation it's a trade-off between architectural design and
business requirements. I recommend to take it as temporary solution until we
find the better one.

Alternatives
------------

Continue to use Watcher scope to segregate resources of cloud cluster.

Another solution is `enhance-watcher-applier-engine`_ blueprint.
Instead of making exact action, we make all the probable actions and give the
decision to Nova Scheduler.

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

Watcher config file should contain filters option with dict of enabled filters
by strategies like:

::

    {"basic": "AvailabilityZoneFilter, DifferentHostFilter",
     "zone_migration": "AvailabilityZoneFilter"}.

By default there should be `AllHostsFilter` associated with every strategy to
pass every virtual machine without limitations.

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  alexchadin

Work Items
----------

* Add documentation page regarding filters
* Update documentation for strategy developers
* Add filter manager to `watcher/decision_engine/manager.py`
* Add affinity/anti-affinity, host aggregates and availability zone filters
* Add unit and functional tests
* Update configuration file to support filters option.

Dependencies
============

None

Testing
=======

Appropriate unit and functional tests should be added.

Documentation Impact
====================

* Add documentation page regarding filters
* Update documentation for strategy developers

References
==========

None

History
=======

None

.. _availability: https://github.com/openstack/nova/blob/stable/queens/nova/scheduler/filters/availability_zone_filter.py#L27
.. _aggregates: https://github.com/openstack/nova/blob/stable/queens/nova/scheduler/filters/aggregate_instance_extra_specs.py#L30
.. _core-compatible: https://github.com/openstack/nova/blob/stable/queens/nova/scheduler/filters/core_filter.py#L79
.. _different: https://github.com/openstack/nova/blob/stable/queens/nova/scheduler/filters/affinity_filter.py#L27
.. _nova-policies: https://review.openstack.org/#/c/329873/
.. _select_destinations: https://github.com/openstack/nova/blob/stable/queens/nova/scheduler/manager.py
.. _enhance-watcher-applier-engine: https://blueprints.launchpad.net/watcher/+spec/enhance-watcher-applier-engine
