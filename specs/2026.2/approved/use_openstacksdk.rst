..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================================
Migrate Watcher to Use OpenStackSDK
===================================

https://blueprints.launchpad.net/watcher/+spec/use-openstacksdk

Watcher currently uses individual Python client libraries (python-novaclient,
python-cinderclient, etc.) to interact with other OpenStack services. These
client libraries have been frozen or deprecated and are scheduled for removal
in future OpenStack releases. This specification proposes migrating Watcher to
use OpenStackSDK, the unified and officially maintained SDK for OpenStack
service interactions, ensuring long-term maintainability. Additionally, this
specification also proposes adding support for Watcher in the OpenStackSDK,
aligning it with most OpenStack projects.

Problem description
===================

Watcher relies on individual Python client libraries to communicate with
various OpenStack services including Cinder, Keystone, Placement, and
others. These libraries face several critical issues:

1. **Deprecation and Removal**: Individual client libraries are no longer
   actively maintained and are scheduled for removal from OpenStack. This
   poses a significant risk to Watcher's continued operation.

2. **Missing features**: The individual client libraries do not support all
   existing functionality. Features introduced in later microversions not
   supported in the client library are not accessible to Watcher.

3. **OpenStack Community Direction**: The OpenStack community has standardized
   on OpenStackSDK as the unified interface for inter-service communication.

Use Cases
---------

**As a Watcher Developer**, I want a unified, consistent API for interacting
with OpenStack services, accessing their complete functionality, reducing code
complexity and improving maintainability.

Proposed change
===============

This specification proposes a phased migration from individual Python client
libraries to OpenStackSDK. The migration will be executed across multiple
release cycles to minimize risk and ensure thorough testing.

Phase 1: Remaining Client Migrations (2026.2)
---------------------------------------------

Following the patterns established in 2026.1, migrate the remaining clients
following the same procedure as done with Nova in this order:

1. **Keystone**: Migrate to ``connection.identity``
2. **Cinder**: Migrate to ``connection.block_storage``
3. **Placement**: Migrate to ``connection.placement``
4. **Ironic**: Migrate to ``connection.baremetal``

Each migration follows the same pattern:

- Add Watcher wrapper objects to the calls to the clients
- Add a configuration group for the service
- Update helper module to use SDK proxy
- Maintain existing interface for backward compatibility
- Update unit tests while keeping the existing asserts to ensure no regressions

Phase 2: Watcher addition to OpenStackSDK (2026.2 or future release)
--------------------------------------------------------------------

Add Watcher service support to OpenStackSDK by contributing an
``infra_optim`` service proxy. This is a longer-term goal that requires:

1. Submit specification to OpenStackSDK project
2. Implement Watcher service proxy in OpenStackSDK
3. Add resource models (Audit, ActionPlan, Strategy, etc.)
4. Implement CRUD operations

Alternatives
------------

One possibility would be to continue using individual client libraries.
This is not viable as the libraries have either stopped development or are
deprecated and will be removed. This would eventually break Watcher entirely.

Another option would be to replace the calls to the client libraries with
direct REST API calls to services. This would imply duplicating functionality
already present in the OpenStackSDK, leading to increased maintenance burden
and effort duplication.

Data model impact
-----------------

None. This change does not modify Watcher's data model or database schema.

REST API impact
---------------

None. This is an internal refactoring that does not change Watcher's REST API.

Security impact
---------------

None. There might be a small gain by reducing the number of dependencies.

Notifications impact
--------------------

None. This change does not affect Watcher's notification system.

Other end user impact
---------------------

None.

Performance Impact
------------------

None. Once all services are migrated, there might be a minimal performance gain
since the number of connections will be reduced, but this will be negligible.

Other deployer impact
---------------------

None. OpenStackSDK is already a dependency since the 2026.1 release.

Developer impact
----------------

Developers will need to learn OpenStackSDK patterns instead of individual
client library APIs. This is a positive change as SDK provides consistent
API patterns across all services and full functionality for the services
integrated.

Future service integrations will use OpenStackSDK exclusively, providing a
clearer pattern than mixing SDK and client libraries.

Upgrade impact
--------------

None. OpenStackSDK was added as an explicit dependency in 2026.1.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  jgilaber

Work Items
----------

1. **Keystone Helper Migration**

   * Create wrapper objects for Keystone objects like services, roles or
     projects
   * Add a [keystone] group in the configuration that can be used to connect to
     the identity service
   * Create keystone_helper.py using SDK identity proxy
   * Update all Keystone-related methods
   * Ensure backward compatibility with existing interface
   * Update existing Keystone helper unit tests

2. **Cinder Helper Migration**

   * Create wrapper objects for Cinder objects like volumes, volume types or
     volume snapshots
   * Add a [cinder] group in the configuration that can be used to connect to
     the block storage service
   * Rewrite cinder_helper.py using SDK block_storage proxy
   * Update all Cinder-related methods
   * Ensure backward compatibility with existing interface
   * Update existing Cinder helper unit tests

3. **Placement Helper Migration**

   * Create wrapper objects for Placement objects like resource providers or
     inventories
   * Add a [placement] group in the configuration that can be used to
     connect to the placement service
   * Rewrite placement_helper.py using SDK placement proxy
   * Update all Placement-related methods
   * Ensure backward compatibility with existing interface
   * Update existing Placement helper unit tests

4. **Ironic Helper Migration**

   * Create wrapper objects for Ironic objects like nodes
   * Add a [ironic] group in the configuration that can be used to connect to
     the baremetal service
   * Rewrite ironic_helper.py using SDK baremetal proxy
   * Update all Ironic-related methods
   * Ensure backward compatibility with existing interface
   * Update existing Ironic helper unit tests

Dependencies
============

This change relies on the OpenStackSDK infrastructure established during the
2026.1 release.

Testing
=======

**Unit Testing**

All existing unit tests for each helper will be updated following the same
pattern established with the Nova helper in 2026.1. Tests will be updated
to use SDK mocks, and their asserts will be maintained to ensure the change
does not introduce any regression.

**Integration Testing**

The existing tempest tests should pass without modification.

Documentation Impact
====================

None.

References
==========

**OpenStack Documentation**

* `OpenStackSDK Documentation <https://docs.openstack.org/openstacksdk/latest/>`_
* `OpenStackSDK Connection from oslo.conf <https://docs.openstack.org/openstacksdk/latest/user/connection.html#from-oslo-conf-conf-object>`_

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - 2026.1
     - Introduced. Nova migration and infrastructure implemented.
   * - 2026.2
     - Re-proposed for Keystone, Cinder, Placement, and Ironic migration.
