..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

========================
Audit tag in VM Metadata
========================

https://blueprints.launchpad.net/watcher/+spec/audit-tag-vm-metadata

Problem description
===================

Watcher optimizes workloads by live migrating VMs. This can be disruptive.
There should be a feature for tenants to opt-in/opt-out some or all of
their VMs from optimization. The solution we propose is to set a VM
metadata "optimize" and watcher strategies should consider only those VMs that
has "optimize" metadata enabled. This feature for strategies to check VM
metadata should be optional and configurable.


Use Cases
---------

As a tenant, I should opt-in/opt-out optimization of my VMs

As a strategy developer, I should be able to filter VMs that are approved
for optimizing

Proposed change
===============

The VMs will have an  "optimize" metadata key.
The compute cluster data model should also store the VM metadata information.
We need to a have a configuration option "check_optimize_metadata" to enable
this feature.

If "check_optimize_metadata" configuration option is enabled, strategy base
class will include only those VMs that has optimize metadata. This will use
the Audit Scope to exclude VMs by metadata.

Example -

.. code-block:: none

     "scope": [
          {"host_aggregates": [
            {"id": 1},
            {"id": 2},
            {"id": 3}
          ]},
          {"availability_zones": [
            {"name": "AZ1"},
            {"name": "AZ2"}
          ]},
          {"exclude": [
            {"instances": [
              {"uuid": "9766dff1-3c81-4de2-92ae-19e0d9adcec6"},
              {"uuid": "777541bb-ce4f-4bf3-8320-d5792d5cdf6e"}
            ]},
            {"instance_metadata": [
              {"optimize": "False"}
            ]},
            {"compute_nodes": [
              {"name": "compute1"}
            ]}
          ]}
        ]



By default "check_optimize_metadata" will be disabled and "optimize"
metadata will not have any effect on the strategies - meaning the strategies
will consider all VMs.


Alternatives
------------



Data model impact
-----------------

There will be changes to the cluster data model to include VM metadata.


REST API impact
---------------


Security impact
---------------

There is no security impact.

Notifications impact
--------------------


Other end user impact
---------------------


Performance Impact
------------------



Other deployer impact
---------------------


Developer impact
----------------


Implementation
==============

Assignee(s)
-----------

Primary assignee:
    hvprash

Other contributors:
    v-francoise
    pradeep-singh-u


Work Items
----------
* Platform owners or automations external to watcher will set the VM Metadata

.. code-block:: none

    # nova meta vm_name set optimize=True

* Enhance the current compute cluster data model to now include the VM
  metadata in its representation.

* Capability in ``Audit Scope`` to exclude by instance_metadata
  (https://github.com/openstack/watcher/blob/54f0758fc3ac47edb4bc3f6eb5e56bf53d4e02f8/watcher/decision_engine/scope/default.py).


* Modify base strategy to filter VMs by metadata based on configuration
  option

.. code-block:: python

    def filter_instances_by_audit_tag(self, instances):
        if not self.config.check_optimize_metadata:
            return instances
        instances_to_migrate = []
        for instance in instances:
            optimize = True
            if instance.metadata:
                try:
                    optimize = strutils.bool_from_string(
                        instance.metadata.get('optimize'))
                except ValueError:
                    optimize = False
            if optimize:
                instances_to_migrate.append(instance)
        return instances_to_migrate


Dependencies
============

N/A

Testing
=======

* Unit tests on watcher `Audit`_ and `Strategy`_
* Unit tests for audit scope. Also tempest scenarios to create an Audit
  Template and define an Audit scope with "instance_metadata"

Documentation Impact
====================

Update documentations and reference to configuration options.

References
==========

N/A

History
=======

N/A

.. _Audit: http://docs.openstack.org/developer/watcher/glossary.html#audit
.. _Strategy: http://docs.openstack.org/developer/watcher/glossary.html#strategies
.. _Audit Scope: https://specs.openstack.org/openstack/watcher-specs/specs/newton/approved/define-the-audit-scope.html
