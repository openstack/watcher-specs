..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==============================
Make Watcher objects versioned
==============================

https://blueprints.launchpad.net/watcher/+spec/watcher-versioned-objects

As we are making Watcher more stable, we now have to tackle the
question of retro-compatibility. Other OpenStack projects already faced this
problem and the community came up with a common answer which is object
versioning.

Below is a non-exhaustive list of blueprint specifications written on the
subject by other projects:

 - https://specs.openstack.org/openstack/oslo-specs/specs/kilo/adopt-oslo-versionedobjects.html
 - https://specs.openstack.org/openstack/heat-specs/specs/kilo/versioned-objects.html


Problem description
===================

As of now, Watcher maintains some (but not all) building blocks previously used
by other projects such as Nova in order to enable the versioning of objects.
As Watcher is now part of the Big Tent, we should start taking into account
backwards compatibility. Moreover, we should standardize the code and therefore
make use of `oslo.versionedobjects`_.

.. _oslo.versionedobjects: http://docs.openstack.org/developer/oslo.versionedobjects/

Use Cases
---------

Whenever existing Watcher objects are created or modified or deleted, the
concerned Watcher objects should see their version bumped whilst indicating
the changes that occurred in order to ease retro-compatibility handling
throughout the codebase.


Proposed change
===============

The focus of this blueprint is to rewrite the Watcher codebase implements its
objects to leverage `oslo.versionedobjects`_ library to enable the versioning
of Watcher objects.

Besides, `oslo.versionedobjects`_ brings along many new field types, among
which ``ObjectField`` can be found. This field can reveal itself useful in
subsequent work about building versioned notifications as we will be most
certainly keen on notifying a more complete set of information that would also
include some data that are directly related to the given Watcher object.
This work will hence be tackled within this blueprint.

Alternatives
------------

- Keep the current codebase and enhance it to support some form of versioning
- Do not support any form of object versioning

Data model impact
-----------------

Add DB relationships on existing models wherever foreign key fields where
already defined:

- The `Strategy`_ will have one ORM relationship field:

  * A ``goal`` field reflecting the ``goal_id`` ForeignKey field

- The `AuditTemplate`_ will have two ORM relationship fields:

  * A ``goal`` field reflecting the ``goal_id`` ForeignKey field
  * A ``strategy`` field reflecting the ``strategy_id`` ForeignKey field

- The `Audit`_ will have two ORM relationship fields:

  * A ``goal`` field reflecting the ``goal_id`` ForeignKey field
  * A ``strategy`` field reflecting the ``strategy_id`` ForeignKey field

- The `ActionPlan`_ will have two ORM relationship fields:

  * A ``audit`` field reflecting the ``audit_id`` ForeignKey field
  * A ``strategy`` field reflecting the ``strategy_id`` ForeignKey field

- The `Action`_ will have one ORM relationship field:

  * An ``action_plan`` field reflecting the ``action_plan_id`` ForeignKey field

- The `EfficacyIndicator`_ will have one ORM relationship field:

  * An ``action_plan`` field reflecting the ``action_plan_id`` ForeignKey field

Moreover, unused DB fields will be removed in order to avoid non
retro-compatible changes as much as possible.


.. _Strategy: http://docs.openstack.org/developer/watcher/glossary.html#strategy
.. _AuditTemplate: http://docs.openstack.org/developer/watcher/glossary.html#audit-template
.. _Audit: http://docs.openstack.org/developer/watcher/glossary.html#audit
.. _ActionPlan: http://docs.openstack.org/developer/watcher/glossary.html#action-plan
.. _Action: http://docs.openstack.org/developer/watcher/glossary.html#action
.. _EfficacyIndicator: http://docs.openstack.org/developer/watcher/glossary.html#efficacy-indicator


REST API impact
---------------

The API design will not be impacted by the ``eager`` flag.
Indeed, API endpoints will not return any eagerly-loaded data.

Security impact
---------------

None.

Notifications impact
--------------------

This work will help building versioned notifications.

Other end user impact
---------------------

None.

Performance Impact
------------------

Loading ``ObjectField`` data makes queries slower. This is the reason why the
concept of eager loading is introduced alongside this blueprint to limit the
associated performance hit to areas where this eager loading is necessary.
Also note that this eager loading will not be cascaded which means that
eagerly loaded related objects will not be subject to eager loading themselves.

Other deployer impact
---------------------

None.

Developer impact
----------------

As objects are being versioned from now on, any modification of an existing
Watcher object should be directly translated into a version bump.
Retro-compatible changes should see the minor version of the related object
bumped whereas any disrupting changes should be translated by a transition to
a new major version.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  vincent-francoise

Work Items
----------

Here below are the changes to be made:

- Enable database loading of ORM relationships in the case of One-to-One and
  One-to-Many foreign keys.
- Add the possibility to either eager load or not the newly added ORM
  relationships for performance purposes.
- Overhaul the code in ``watcher/objects/base.py`` to now use
  `oslo.versionedobjects`_.
- Update all Watcher objects which had foreign key fields to add
  ``ObjectField`` fields that will have to be filled whenever an eager loading
  of the underlying DB model is requested.

Dependencies
============

None.

Testing
=======

Apart from updating existing unit test suites, this blueprint does not bring
any new end-user functionality. Hence, the current set of Tempest test should
remain unchanged and still pass upon completion.

Documentation Impact
====================

The DB schema shown in the architecture will have to be updated.

References
==========

None.

History
=======

None.
