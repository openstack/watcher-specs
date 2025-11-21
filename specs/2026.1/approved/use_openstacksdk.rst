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
various OpenStack services including Nova, Cinder, Keystone, Placement, and
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

Phase 1: Nova Client Migration + Infrastructure (2026.1)
--------------------------------------------------------

The initial phase establishes the OpenStackSDK infrastructure and migrates
the most used service in Watcher: Nova.

**Infrastructure Setup**

1. Add OpenStackSDK as a dependency in requirements.txt

2. Add a helper function in ``watcher/common/clients.py`` to
   create and manage an OpenStackSDK Connection object. This connection will be
   established either using a keystone session like it's currently done with
   the individual clients, or using a RequestContext, authenticating via the
   auth_token it contains.

**Nova Helper Migration**

1. Modify the existing Nova client implementation in
   ``watcher/common/nova_helper.py`` so that they return Watcher objects
   representing compute concepts like server, hypervisor or flavor, instead of
   the python-novaclient objects.

2. Modify the nova_helper to optionally accept a Connection object, if that is
   not passed, it will use the helper function introduced in the previous
   section to create a connection.

3. Replace the calls to python-novaclient with calls to the Compute SDK. The
   methods will maintain the functionality and the interface introduced in the
   previous step.

Phase 2: Other Client Migrations (2026.1 or Future)
---------------------------------------------------

Following the patterns established in Phase 1, migrate the remaining clients
following the same procedure as done with Nova in this order:

1. **Keystone**: Migrate to ``connection.identity``
2. **Cinder**: Migrate to ``connection.block_storage``
3. **Placement**: Migrate to ``connection.placement``
4. **Ironic**: Migrate to ``connection.baremetal``

Each migration follows the same pattern:

- Update helper module to use SDK proxy
- Maintain existing interface for backward compatibility
- Update unit tests while keeping the existing asserts to ensure no regressions

Phase 3: Watcher addition to OpenStackSDK (Future)
--------------------------------------------------

Add Watcher service support to OpenStackSDK by contributing an
``infra_optim`` service proxy. This is a longer-term goal that requires:

1. Submit specification to OpenStackSDK project
2. Implement Watcher service proxy in OpenStackSDK
3. Add resource models (Audit, ActionPlan, Strategy, etc.)
4. Implement CRUD operations

Phase 4: python-watcherclient Integration (Future)
--------------------------------------------------

Update python-watcherclient to reflect watcher support in the sdk:

1. Deprecate python-watcherclient library in favor of the SDK
2. Deprecate watcher cli in favor of the OpenStackClient plugin, the plugin
   will stay in the python-watcherclient repository

Phase 5: Watcherclient consumers migration (Future)
---------------------------------------------------

Once the Watcher service is integrated in the OpenStackSDK, all consumers of
the python-watcherclient should be migrated to use the new OpenStackSDK Watcher
Proxy. This includes the watcher-dashboard horizon plugin and the
rally-openstack project.

Phase 6: Cleanup and Deprecation (Future)
-----------------------------------------

After all previous phases are completed, and once all consumers of
python-watcherclient have removed its usage, the deprecated code from the
python-watcherclient can be removed.

Scope of 2026.1 Implementation
-------------------------------

This specification focuses on **Phase 1 only** for the 2026.1 release:

- OpenStackSDK infrastructure setup
- Nova client migration
- Testing framework establishment

Subsequent phases will be addressed in future specifications once Phase 1
patterns are validated.

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

None. OpenStackSDK will be added as a dependency. This is included in
standard OpenStack distributions and should not require special packaging
effort.

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

None. OpenStackSDK will be added as an explicit dependency. However, it should
already be present in existing developments since its a dependency of
python-openstackclient.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  jgilaber

Work Items
----------

1. **Infrastructure Setup**

   * Add openstacksdk to requirements.txt
   * Extend OpenStackClients class with Connection property

2. **Nova Helper Migration**

   * Rewrite nova_helper.py using SDK compute proxy
   * Update all Nova-related methods
   * Ensure backward compatibility with existing interface
   * Update existing Nova helper unit tests

Dependencies
============

This change introduces the openstacksdk library as a dependency for watcher.
It will also remove python-openstackclient as a dependency since it's not
currently used by Watcher.

Testing
=======

**Unit Testing**

All existing unit tests for Nova helper will be updated to use new objects
representing compute objects. After that change, when the Nova helper is moved
to use the SDK, the tests will also be updated to use SDK mocks, and their
asserts will be maintained to ensure the change does not introduce any
regression.

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
     - Introduced
