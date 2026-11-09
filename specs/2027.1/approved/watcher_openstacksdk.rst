..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================================
Migrate Watcher to Use OpenStackSDK
===================================

https://blueprints.launchpad.net/watcher/+spec/watcher-openstacksdk

Watcher currently uses individual Python client libraries (python-novaclient,
python-cinderclient, etc.) to interact with other OpenStack services. These
client libraries have been frozen or deprecated and are scheduled for removal
in future OpenStack releases. This specification proposes migrating Watcher to
use OpenStackSDK, the unified and officially maintained SDK for OpenStack
service interactions, ensuring long-term maintainability. Additionally, this
specification proposes adding support for Watcher in the OpenStackSDK,
aligning it with most OpenStack projects.

This is the third iteration of a multi-cycle, phased migration effort. The
2026.1 release added openstacksdk as a dependency, established the SDK
infrastructure in ``watcher/common/clients.py``, and migrated the Nova
helper. The 2026.2 release migrated the Keystone, Cinder, and Placement
helpers; the Ironic helper migration was planned but not completed within the
cycle. During the 2027.1 PTG [1]_, the Ironic integration was discussed and the
conclusion was that the lack of test coverage and limited usage of the helper
across the code base do not justify the effort of migrating it to the SDK.
This 2027.1 specification therefore proposes: deprecating the Ironic
integration and making python-ironicclient an optional dependency (Phase 1),
contributing a ``resource-optimization`` service proxy to the upstream
OpenStackSDK project (Phase 2), and, as a stretch goal contingent on Phase 2
completion, beginning migration of python-watcherclient consumers to the new
SDK proxy (Phase 3).

Problem Description
===================

Watcher relies on individual Python client libraries to communicate with
various OpenStack services. By the start of the 2027.1 cycle, all service
helpers except the Ironic one have been migrated to OpenStackSDK. The
remaining Ironic integration poses a specific problem:

1. **Lack of test coverage**: The ``saving_energy`` strategy and the
   baremetal data model collector, which are the primary consumers of
   ``ironic_helper.py``, have no functional or integration test coverage.
   This makes it impossible to validate any change to the Ironic code path
   with confidence.

2. **Limited usage**: The Ironic integration in Watcher is only used in one
   strategy and not known to be widely deployed. The effort required to safely
   migrate it to the SDK cannot be justified given the limited evidence of
   active use.

3. **Hard dependency on python-ironicclient**: Watcher currently lists
   python-ironicclient as a hard dependency, meaning all Watcher deployments
   must install it even when no baremetal workloads are managed.

In addition to Watcher's own consumption of client libraries, Watcher is not
yet exposed through the OpenStackSDK. Unlike most OpenStack services, there
is no ``resource-optimization`` proxy in the SDK, so other projects and end
users cannot interact with Watcher through the unified SDK and must instead
depend on the standalone python-watcherclient library. This is inconsistent
with the rest of the ecosystem and forces consumers such as watcher-dashboard
and rally-openstack to maintain a dependency on a service-specific client.

At the start of the 2027.1 cycle the state of the migration is:

* Nova, Keystone, Cinder, and Placement helpers have been migrated to the
  SDK.
* The Ironic helper still uses python-ironicclient. After PTG discussion,
  the decision was made to deprecate the Ironic integration rather than
  migrate it.
* No Watcher proxy exists in OpenStackSDK.

Use Cases
----------

**As a Watcher developer**, I want the Ironic integration to be clearly
marked as deprecated so that I know not to invest further work in it, and I
want python-ironicclient to be an optional dependency so that Watcher's
dependency footprint is reduced for deployments that do not use baremetal.

**As an OpenStack developer of another project (e.g. watcher-dashboard or
rally-openstack)**, I want to interact with Watcher through the OpenStackSDK
like I do with other OpenStack services, instead of depending on the
service-specific python-watcherclient library.

**As an OpenStack end user or operator**, I want to manage Watcher audits,
audit templates, action plans, and actions through the same unified SDK I
already use for the rest of my cloud, benefiting from consistent
authentication, service discovery, and resource handling.

Proposed Change
===============

This specification continues the phased migration from individual Python
client libraries to OpenStackSDK. The work for the 2027.1 cycle is organized
into three phases. Phase 1 and Phase 2 are the committed scope for the cycle.
Phase 3 is an explicit stretch goal that will only be started if Phase 2 is
completed during the cycle with sufficient time remaining.

Phase 1 (required): Deprecate Ironic Integration
-------------------------------------------------

Rather than migrating the Ironic helper to OpenStackSDK, this phase
deprecates the entire Ironic integration in Watcher. The scope of the
deprecation covers ``ironic_helper.py`` and the baremetal data model
collector. The approach is:

1. Emit a deprecation warning whenever the Ironic-related code paths are
   exercised at runtime: when the baremetal collector is loaded and when
   ``ironic_helper.py`` is instantiated.

2. Move the ``import ironicclient`` statements inside the functions that
   use them (lazy import), and wrap them with a clear ``UnsupportedError``
   message directing operators to install python-ironicclient explicitly
   if they still need baremetal support during the deprecation period.

3. Remove python-ironicclient from ``requirements.txt`` and add it to
   ``extras_require`` or equivalent, so that it becomes an optional
   dependency that must be installed explicitly by operators who rely on
   the Ironic integration.

4. Update the release notes to document the deprecation and the expected
   removal timeline.

Phase 2 (required): Watcher Proxy in OpenStackSDK
-------------------------------------------------

This phase adds Watcher service support to OpenStackSDK by contributing a
``resource-optimization`` service proxy. This enables other OpenStack
projects and end users to interact with Watcher through the unified SDK,
aligning Watcher with the rest of the ecosystem. The work involves:

1. Submit a specification/patch to the OpenStackSDK project proposing the
   ``resource-optimization`` proxy, following the OpenStackSDK contribution
   process.

2. Implement the Watcher service proxy (``resource-optimization``) in
   OpenStackSDK.

3. Add resource models for the Watcher objects exposed by the Watcher REST
   API: ``Audit``, ``AuditTemplate``, ``ActionPlan``, ``Action``, ``Goal``,
   ``Strategy``, ``ScoringEngine``, ``Service``, and ``DataModel``.

4. Implement the CRUD operations for these resources following OpenStackSDK
   patterns (list, get, create, update, delete as appropriate for each
   resource, matching the operations exposed by the Watcher API).

5. Add proper service discovery and endpoint handling so the proxy resolves
   the ``infra-optim`` service type from the service catalog and honors
   Watcher API microversion negotiation.

The resource models and operations must mirror the existing Watcher REST API
so the SDK is a faithful representation of the service. Where the Watcher
API supports microversions, the proxy must support requesting them.

Phase 3 (stretch goal): Migrate python-watcherclient Consumers
--------------------------------------------------------------

This phase is a **stretch goal** and will only be undertaken if Phase 2 is
completed during the 2027.1 cycle with enough time remaining. It is
explicitly contingent on the ``resource-optimization`` proxy being merged and
available in OpenStackSDK.

Once the Watcher proxy is available, begin migrating consumers of
python-watcherclient to use the new SDK proxy:

1. **watcher-dashboard** (the Horizon plugin): replace its usage of
   python-watcherclient with the OpenStackSDK ``resource-optimization`` proxy.

2. **rally-openstack**: replace its usage of python-watcherclient with the
   OpenStackSDK ``resource-optimization`` proxy.

Because this is a stretch goal, its acceptance criteria are limited to
whatever consumer migrations can be reasonably completed and reviewed within
the cycle. Any consumer migration not completed in 2027.1 will be
re-proposed in a future cycle. This phase does not block the completion of
Phases 1 and 2.

Alternatives
------------

The original plan (carried from 2026.2) was to migrate the Ironic helper to
OpenStackSDK following the same pattern used for the other helpers. This was
rejected during the 2027.1 PTG because the ``saving_energy`` strategy and
the baremetal collector lack functional test coverage, making it impossible
to validate the migration with confidence, and because the integration is
not known to be widely deployed. Investing the effort to migrate poorly
tested and lightly used code was deemed unjustifiable.

Keeping the Ironic integration unchanged and continuing to carry
python-ironicclient as a hard dependency was also considered. This is
rejected because it perpetuates a maintenance burden with no corresponding
benefit and because the dependency will eventually be removed from
OpenStack, which would break Watcher.

An alternative to contributing the ``resource-optimization`` proxy upstream
would be to keep python-watcherclient as the only programmatic interface to
Watcher indefinitely. This is rejected because it perpetuates the
divergence from the rest of the OpenStack ecosystem, forces consumers to
maintain a service-specific dependency, and leaves Watcher unable to
benefit from the shared maintenance, testing, and features of the SDK.

Data Model Impact
-----------------

None. This change does not modify Watcher's data model or database schema.
The resource models added in Phase 2 live in the OpenStackSDK project and
describe the existing Watcher REST API resources; they do not introduce new
Watcher data model entities.

REST API Impact
---------------

None. The Phase 1 deprecation is internal and does not change Watcher's
REST API. The Phase 2 ``resource-optimization`` proxy is a new consumer of
Watcher's existing REST API implemented in OpenStackSDK; it does not add or
modify any Watcher API endpoint. The proxy must, however, correctly consume
Watcher's existing microversioned API.

Security Impact
---------------

None. Making python-ironicclient optional reduces the mandatory dependency
surface of Watcher.

Notifications Impact
--------------------

None.

Other End User Impact
---------------------

The Phase 1 deprecation is visible to operators who use the
``saving_energy`` strategy, the baremetal data model collector, or the
``change_node_power_state`` action: they will see deprecation warnings at
runtime and must install python-ironicclient explicitly once it is removed
from Watcher's hard dependencies. The ``change_node_power_state`` action is
called out explicitly because the ``actuator`` strategy lets users build an
action plan from a chosen list of existing actions and their parameters, so
this Ironic-backed action can be invoked directly and not only through the
``saving_energy`` strategy.

The Phase 2 work has a positive end user impact: once the
``resource-optimization`` proxy is available in OpenStackSDK, end users and
operators can manage Watcher resources through the unified SDK rather than
depending on python-watcherclient.

Performance Impact
------------------

None.

Other Deployer Impact
---------------------

Operators using the ``saving_energy`` strategy, the baremetal data model
collector, or the ``change_node_power_state`` action (which can be selected
directly through the ``actuator`` strategy) will see deprecation warnings at
runtime. They must also install python-ironicclient explicitly once it is
removed from Watcher's ``requirements.txt``, as it will no longer be pulled
in automatically. The Phase 2 and Phase 3 work happens in the OpenStackSDK,
watcher-dashboard, and rally-openstack projects respectively and does not
impose additional deployment requirements on the Watcher service.

Developer Impact
----------------

The deprecation of the Ironic integration signals to developers that no new
work should be added to the baremetal code paths. The Ironic helper, the
baremetal collector, and the ``saving_energy`` strategy are on a path to
removal in a future cycle.

The Phase 2 proxy gives OpenStack developers a standard, SDK-based way to
interact with Watcher, which will become the recommended integration path
for new consumers.

Upgrade Impact
--------------

Operators using the Ironic integration must install python-ironicclient
explicitly after this change, as it will no longer be a hard dependency of
Watcher. A deprecation warning will guide them. Existing continuous audits that
rely on the Ironic integration (for example one running the
``saving_energy`` strategy) keep working as long as python-ironicclient is
installed, emitting deprecation warnings on each run. If the now-optional
dependency is not installed, the Ironic code path raises the
``UnsupportedError`` described in Phase 1, so such audits fail at runtime
until python-ironicclient is added back. No audit definitions, templates, or
action plans need to be changed.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  jgilaber

Work Items
----------

1. **Deprecate Ironic Integration (Phase 1, required)**

   * Add deprecation warnings to ``ironic_helper.py`` and the baremetal data
     model collector
   * Convert ``import ironicclient`` to a lazy import inside the functions
     that use it, with a clear ``UnsupportedError`` message
   * Remove python-ironicclient from ``requirements.txt`` and add it as an
     optional/extras dependency
   * Add a release note documenting the deprecation and the expected removal
     timeline

2. **Watcher Proxy in OpenStackSDK (Phase 2, required)**

   * Submit a specification/patch to the OpenStackSDK project for the
     ``resource-optimization`` proxy
   * Implement the ``resource-optimization`` service proxy in OpenStackSDK
   * Add resource models for ``Audit``, ``AuditTemplate``, ``ActionPlan``,
     ``Action``, ``Goal``, ``Strategy``, ``ScoringEngine``, ``Service``,
     and ``DataModel``.
   * Implement CRUD operations for each resource following OpenStackSDK
     patterns
   * Add service discovery and endpoint handling, including Watcher API
     microversion support
   * Add unit and functional tests in OpenStackSDK following its conventions

3. **Migrate python-watcherclient Consumers (Phase 3, stretch goal)**

   .. note::

      The following work items are a stretch goal and are contingent on the
      completion of Phase 2 during the cycle. They will only be started if
      the ``resource-optimization`` proxy is available and time remains in
      the 2027.1 cycle.

   * Migrate watcher-dashboard (Horizon plugin) to use the OpenStackSDK
     ``resource-optimization`` proxy instead of python-watcherclient
   * Migrate rally-openstack to use the OpenStackSDK
     ``resource-optimization`` proxy instead of python-watcherclient

Dependencies
============

Phase 1 has no external dependencies. See the previous specifications for
context on the overall migration effort:

* 2026.1 spec (implemented):
  ``specs/2026.1/implemented/use_openstacksdk.rst``
* 2026.2 spec (implemented):
  ``specs/2026.2/implemented/use_openstacksdk.rst``

Phase 2 depends on acceptance by the OpenStackSDK project of the proposed
``resource-optimization`` proxy specification and patches; the timeline is
therefore partly outside the control of the Watcher team.

Phase 3 (stretch goal) depends on the successful completion and
availability of Phase 2, and on coordination with the watcher-dashboard and
rally-openstack projects.

Testing
=======

**Unit Testing**

The existing unit tests for the Ironic helper and the baremetal collector
will be updated to verify that the deprecation warnings are emitted at the
correct points and that the lazy import raises a clear ``UnsupportedError``
(wrapping the underlying ``ImportError``) with the install-guidance message
when python-ironicclient is not installed.

For Phase 2, the ``resource-optimization`` proxy and its resource models
will be covered by unit and functional tests in the OpenStackSDK project,
following that project's testing conventions (proxy tests and resource tests
for each Watcher resource, plus functional tests exercising the proxy
against a real Watcher service where the OpenStackSDK gate provides one).

**Integration Testing**

The existing Watcher tempest tests should pass without modification. Any
tempest tests that exercise the Ironic-related code paths will be updated
to reflect the deprecation.

**Stretch Goal Testing**

If Phase 3 is undertaken, the migrated consumers (watcher-dashboard and
rally-openstack) will be validated using their respective existing test
suites, ensuring the switch from python-watcherclient to the SDK proxy does
not introduce regressions.

Documentation Impact
====================

The deprecation of the Ironic integration must be documented in the release
notes. The existing configuration reference for the Ironic-related options
should be annotated with the deprecation notice.

For Phase 2, the ``resource-optimization`` proxy will be documented within
the OpenStackSDK project following its documentation conventions (proxy
reference and resource reference pages).

References
==========

**Previous Specifications**

* 2026.1 spec, introducing the migration and the Nova helper:
  ``specs/2026.1/implemented/use_openstacksdk.rst``
* 2026.2 spec, migrating Keystone, Cinder, Placement, and (planned) Ironic:
  ``specs/2026.2/implemented/use_openstacksdk.rst``

**OpenStack Documentation**

* `OpenStackSDK Documentation
  <https://docs.openstack.org/openstacksdk/latest/>`_
* `OpenStackSDK Connection from oslo.conf
  <https://docs.openstack.org/openstacksdk/latest/user/connection.html#from-oslo-conf-conf-object>`_
* `OpenStackSDK Contributor Documentation
  <https://docs.openstack.org/openstacksdk/latest/contributor/index.html>`_

**2027.1 PTG discussion**

* .. [1] https://etherpad.opendev.org/p/watcher-2027.1-ptg#L392

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
       Keystone, Cinder, and Placement completed; Ironic not completed.
   * - 2027.1
     - Ironic migration dropped in favor of deprecating the Ironic
       integration and making python-ironicclient optional. Added the
       ``resource-optimization`` proxy to OpenStackSDK (Phase 2), and
       (stretch goal) migrating python-watcherclient consumers to the new
       SDK proxy (Phase 3).
