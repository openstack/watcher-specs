..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==============================
Exclude Project by Audit Scope
==============================

https://blueprints.launchpad.net/watcher/+spec/audit-scope-exclude-project

Problem description
===================

Watcher using audit scope can exclude instances, compute nodes, host
aggregates, instance metadata from Compute CDM but as of now it can not
exclude project from compute CDM.

Use Cases
----------

As a Cloud Administrator sometimes I want to exclude one or more projects
out of audit scope. There can be many reasons to exclude some projects out
of audit scope e.g SLA requirement, projects running some critical
applications etc.

Proposed change
===============

This spec proposes to add feature exclude project from compute CDM.
To implement this feature the following things need to be done

  * Add project_id in compute CDM, project_id will be added in
    Instance element of compute CDM.
    example xml refernce of Instance element of compute CDM:

     <Instance state="active" human_id="" uuid="INSTANCE_0" vcpus="10"
      disk="20" disk_capacity="20" memory="2"
      metadata='{"optimize": true,"top": "floor", "nested": {"x": "y"}}'/>

  * Add exclude project logic in compute CDM

Alternatives
------------

None.

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

python-watcherclient help message will be updated.
watcher-dashboard should also be updated.

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
  <adi-sky17>

Other contributors:
  <nakamura-h>

Work Items
----------

* Add project_id field in Instance element of Compute CDM
  watcher/decision_engine/model/element/instance.py

* Get instance project_id information while building instance model
  watcher/decision_engine/model/collector/nova.py

* Add logic for excluding instances with specified project id from
  audit scope in compute scope
  watcher/decision_engine/scope/compute.py

* Update help message in python-watcherclient

Dependencies
============

None

Testing
=======

Unit test will be added.

Documentation Impact
====================

None

References
==========

None

History
=======

None
