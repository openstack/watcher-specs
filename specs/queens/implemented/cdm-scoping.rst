..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Define a tailored Scoper for each CDM
==========================================

https://blueprints.launchpad.net/watcher/+spec/cdm-scoping

Problem description
===================

Storage cluster data model was introduced in Pike cycle. Since the model is
different from compute data model, current single CDM scoper does not work
for the model.

Use Cases
----------

As a Watcher user, I want to restrict scope of storage cluster data model.

Proposed change
===============

* Add _audit_scope instance attribute to the BaseClusterDataModelCollector
  and initialize when instantiated.

* Remove audit_scope_handler from the current BaseStrategy and move it within
  the BaseClusterDataModelCollector.

* Add audit_scope argument to CollectorManager's get_cluster_model_collector
  method.

* Change compute_model method to use Collector's audit_scope_handler.

* Change original DefaultScope.

  * get_scoped_model simply returns cluster_model.

  * For representing multi data model for JSON shema, we change DEFAULT_SCHEMA
    as the following::

      DEFAULT_SCHEMA = {
          "$schema": "http://json-schema.org/draft-04/schema#",
          "type": "object",
          "properties": {
              "compute": {
                  # current JSON schema moved to NovaClusterDataModelCollector
                  # retrieved from NovaClusterDataModelCollector
              },
              "storage": {
                  # retrieved from CinderClusterDatamodelCollector
              },
              .......
          }
      }

    Properties are dynamically retrieved from collector plugins.

  * Update validate method in AuditTemplatePostType in accordance with the
    above change.

* Rename the DefaultScope as ComputeScope and override the audit_scope_handler
  property in the Compute Collector.

* Change audit template help message in python-watcherclient.

Alternatives
------------

None

Data model impact
-----------------

None

REST API impact
---------------

Scope JSON schema definition for the audit template POST data from
the request body will be changed in accordance with DEFAULT_SCHEMA change.

Security impact
---------------

None

Notifications impact
--------------------

None

Other end user impact
---------------------

End user defines audit scope in each audit template by specifying yaml or json
file with --scope option. The file format will be changed according to JSON
schema change.

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
  <nakamura-h>

Other contributors:
  <None>

Work Items
----------

* Add or remove audit_scope and audit_scope_handler from/to base classes.

* Change original DefaultScope.

* Change Compute Collector to use ComputeScope instead of DefaultScope.

* Change python-watcherclient.

Dependencies
============

None

Testing
=======

Unit test will be updated.

Documentation Impact
====================

None, but it is preferable to adding more.

References
==========

* https://blueprints.launchpad.net/watcher/+spec/cinder-model-integration
