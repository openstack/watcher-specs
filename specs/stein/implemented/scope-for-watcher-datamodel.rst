..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================================
Adding scope for Watcher data model
===================================

https://blueprints.launchpad.net/watcher/+spec/scope-for-watcher-datamodel


Problem description
===================

For a large cloud infrastructure, such as CERN, there are more than
10k servers, retrieving data from Nova to build Watcher compute
data model may take a long time. If the audit is just for a subset
of all nodes, it's better to get the data from the nodes that audit needs.

Use Cases
----------

As a Watcher user, I want that Watcher doesn't build compute data model before
creating audit.
As a Watcher user, I want that Watcher build compute data model according to
the scope of audit.


Proposed change
===============

As now, Watcher builds compute data model when starting the Decision Engine.
And there is a periodic task to rebuild the data model.
To avoid building the data model before creating audit, we need to check a
flag before building the data model.
for example:

.. code-block:: python

    def execute(self):
        """Build the compute cluster data model"""
        if self._audit_scope_handler is None:
            LOG.debug("No audit, Don't Build compute data model")
            return

        builder = ModelBuilder(self.osc)
        return builder.execute(self._data_model_scope)


Audit scope is a optional parameter when creating audit. If user don't
set a scope ,the default scope is empty, it means this audit used for
all nodes.
An example of the audit scope:

.. code-block:: python

    {"compute":
        [{"host_aggregates": [
                              {"id": 1},
                              {"id": 2},
                              {"id": 3}]},
         {"availability_zones": [
                              {"name": "AZ1"},
                              {"name": "AZ2"}]},
    }

When building the data model according to audit scope, there are some cases
need to be considered:

no data model, audit scope is empty
-----------------------------------
* It's the first time to build the data model. Because audit scope is empty,
  the data model should include all the nodes.

no data model, audit scope is not empty
---------------------------------------
* It's the first time to build the data model according to audit scope.

Existing data model, new audit scope is empty
---------------------------------------------
* If the data model has included all nodes, it will not be rebuilt.

* If the data model doesn't include all nodes, it will be rebuilt.

existing data model, new audit scope is not empty
-------------------------------------------------
* If the nodes specified in scope are already included in the data model,
  it will not be rebuilt.

* If the nodes specified in the scope aren't included in the data model,
  it will be rebuilt.


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

This will reduce the impact on system performance, especially for
large cloud infrastructure.

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
  <licanwei>

Work Items
----------

* Add a check to the audit to create before building the data model.

* Add the model scope to record the audit scope in the ModelBuilder class.

* Update the data model according to the audit scope.


Dependencies
============

None


Testing
=======

Add unit tests.


Documentation Impact
====================

Update Watcher developer documents.


References
==========

None


History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Stein
     - Introduced

