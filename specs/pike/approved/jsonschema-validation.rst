..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================================================================
Remove voluptuous and Use JSONSchema as our only JSON validation tool
=====================================================================

https://blueprints.launchpad.net/watcher/+spec/jsonschema-validation

As of now in Watcher, both JSONSchema and voluptuous are used to validate
JSON payloads. However, the structure of voluptuous is not standardized
compared to JSONSchema. This problem of voluptuous makes it troublesome
to expose the validation schema through our API. So we want to remove
existing voluptuous validation and use JSONSchema as our only JSON
validation tool to validate JSON payloads.

Problem description
===================

This blueprint will replace existing voluptuous validation with JSONSchema
in watcher and use JSONSchema as the only JSON validation tool to validate
JSON payloads.

Use Cases
---------

As a developer, I want to have a consistent and standard JSON payload
validation system which will make it easier to combine all the validation
schemas together and expose them through API later.

Proposed change
===============

For each Watcher action, we need to introduce a new JSONSchema to validate
its input parameters when it gets to the Applier.

We need to introduce new JSONSchemas to validate the efficacy indicators.

Alternatives
------------

We can also use voluptuous validation as our only validation tool, however
voluptuous is not standardized compared to JSONSchema.

Data model impact
-----------------

The incoming request is represented as an object, in which case the request
object would have the jsonschema validator as an attribute.

This blueprint should not require a database migration or database
schema change.

REST API impact
---------------

This has an impact in the API because it changes the display format
of efficacy specification.

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

None

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:

 Yumeng Bao <yumeng+bao>

Work Items
----------

* Remove voluptuous schemas
As of now, voluptuous is used to:
- validate the input parameters of a Watcher action when it gets to the
Applier.
- validate the efficacy indicators
* Implement jsonschemas to validate the efficacy indicators and the input
parameter of action in Watcher Applier.
* Implement appropriate unit tests to test various scenarios.


Dependencies
============

None expected

Testing
=======

Appropriate unit tests will be adapted to new changes.

Documentation Impact
====================

It will be necessary to add new content relating to this change.

References
==========

https://blueprints.launchpad.net/watcher/+spec/jsonschema-validation
https://python.libhunt.com/project/jsonschema/vs/voluptuous

History
=======

No history
