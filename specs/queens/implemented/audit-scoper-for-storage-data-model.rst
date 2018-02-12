..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================================
Audit scoper for storage data model
===================================

https://blueprints.launchpad.net/watcher/+spec/audit-scoper-for-storage-data-model

Problem description
===================

Storage cluster data model was introduced in Pike cycle. Since the model is
different from compute data model, we need CDM scoper for storage cluster
data model.

Use Cases
----------

As a Watcher user, I want to restrict scope of storage cluster data model.

Proposed change
===============

This spec adds storage cluster data model scoper which can restrict
the followings.

* storage availability zone

* volume type

* exclude

  * volume

  * storage pools

  * volumes of project

For adding it, we will implement as compute cluster data model scoper is
implemented.

* Add JSON schema in cinder cluster data model collector.

* Add storage audit scope handler which overrides BaseScope class
  and implements get_scoped_model method.

Alternatives
------------

Strategy developer can restrict storage cluster data model
in a strategy respectively.

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

End user can define audit scope for storage cluster data model in audit
template by specifying yaml or json file with --scope option in the same manner
for compute cluster data model.

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

* Add JSON schema in cinder cluster data model collector.

* Add storage audit scope handler which overrides BaseScope class
  and implements get_scoped_model method.


Dependencies
============

None

Testing
=======

Unit test will be added.

Documentation Impact
====================

Update the help message in python-watcherclient, provide details how to add
scope for storage data model.

References
==========

None

History
=======

None
