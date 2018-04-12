..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=========================
API validation using JSON
=========================

https://blueprints.launchpad.net/watcher/+spec/api-validation


Problem description
===================

Currently Watcher doesn't have a consistent request validation layer.
User can change some fields that are not supposed to be changed. For example
user can update any value in audit_type field of an Audit object, Its valid
value should only be 'ONESHOT' or 'CONTINUOUS'. We need to restrict fields to
update in Audit Object. Ideally, watcher should have some validation in place
to catch disallowed parameters and return a validation error to the user.

Use Cases
----------

As a user or developer, I want to observe consistent API validation and values
passed to the Watcher API server.


Proposed change
===============

One possible way to validate the Watcher API is to use jsonschema_ similar to
Nova, Keystone and Glance).A jsonschema validator object can be used to check
each resource against an appropriate schema for that resource. If the
validation passes, the request can follow the existing flow of control through
the resource manager to the backend. If the request body parameters fails the
validation specified by the resource schema, a validation error wrapped in
HTTPBadRequest will be returned from the server.

Example:
"Invalid input for field 'name'. The value is 'some invalid name value'.

Each API definition should be added with the following ways:

* Create definition files under ./watcher/api/schemas/.
* Each definition should be described with JSON Schema.
* Each parameter of definitions(type, minLength, etc.) can be defined from
  current validation code, DB schema, unit tests, or so on.

Some notes on doing this implementation:

* Common parameter types can be leveraged across all watcher resources. An
  example of this would be as follows::

    from watcher.api.validation import parameter_types
    # audit create schema
    create = {
        'type': 'object',
        'properties': {
             'goal': parameter_types.uuid,
             'strategy': parameter_types.uuid,
             'name': parameter_types.name,
             'audittemplate': {'type': ['string']}
        }
        'oneOf':[{'required': ['goal','strategy']},{'required': ['audittemplate']}]
        'additionalProperties': False,
    }

    parameter_types.py:

    name = {
        'type': 'string', 'minLength': 0, 'maxLength': 255,
    }

    uuid = {
        'type': 'string', 'format': 'uuid'
    }

    # This registers a FormatChecker on the jsonschema module.
    # It might appear that nothing is using the decorated method but it gets
    # used in JSON schema validations to check uuid formatted strings.
    from oslo_utils import uuidutils

    @jsonschema.FormatChecker.cls_checks('uuid')
    def _validate_uuid_format(instance):
        return uuidutils.is_uuid_like(instance)

* The validation can take place at the controller layer using below decorator::

    from watcher.api.schemas import plans as plan

    @validation.schema(audit.create)
    def create(self, req, body):
        """Creates a new audit."""


* When adding a new API resources to watcher, the new resource must be proposed
  with its appropriate schema.


Alternatives
------------

Before the API validation framework, we need to add the validation code into
each API method in ad-hoc. These changes would make the API method code messy
and we needed to create multiple patches due to incomplete validation.

If using JSON Schema definitions instead, acceptable request formats are clear
and we don’t need to do ad-hoc works in the future.

Data model impact
-----------------

None

REST API impact
---------------

API Response code changes:

There are some occurrences where API response code will change while adding
schema layer for them. For Example, In "goal show API" for if we pass as
invalid uuid, then it fails with 404 resource not found. For this we can apply
validation on uuid, that uuid should be in uuid format. If user passes an
invalid uuid, he/she will get 400 BadRequest in response.

Security impact
---------------

The output from the request validation layer should not compromise data or
expose private data to an external user. Request validation should not
return information upon successful validation. In the event a request
body is not valid, the validation layer should return the invalid values
and/or the values required by the request, of which the end user should know.
The parameters of the resources being validated are public information,
described in the Watcher API spec, with the exception of private data.
In the event the user's private data fails validation, a check can be built
into the error handling of the validator to not return the actual value of the
private data.

jsonschema documentation notes security considerations for both schemas and
instances:
http://json-schema.org/latest/json-schema-core.html#anchor21

Better up front input validation will reduce the ability for malicious user
input to exploit security bugs.

Notifications impact
--------------------

None

Other end user impact
---------------------

None

Performance Impact
------------------

Watcher will pay some performance cost for this comprehensive request
parameters validation, because the checks will be increased for API parameters
which are not validated now.


Other deployer impact
---------------------

None

Developer impact
----------------

This will require developers contributing new extensions to Watcher to have
a proper schema representing the extension's API.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <rajat29>

Other contributors:
  <adi-sky17>

Work Items
----------

#. Initial validator implementation, which will contain common validator code
   designed to be shared across all resource controllers validating request
   bodies.
#. Introduce validation schemas and Enforce validation for "Audit API".
#. Introduce validation schemas and Enforce validation for "Action API".
#. Introduce validation schemas and Enforce validation for "Audittemplate API"
#. Introduce validation schemas and Enforce validation for "Action plan API".
#. Remove duplicated ad-hoc validation code.
#. Add unit and end-to-end tests of related APIs.
#. Add/Update Watcher documentation.


Dependencies
============

None


Testing
=======

Tempest tests can be added as each resource is validated against its schema.
These tests should walk through invalid request types.


Documentation Impact
====================

#. The Watcher API documentation will need to be updated to reflect the
   REST API changes.
#. The Watcher developer documentation will need to be updated to explain
   how the schema validation will work and how to add json schema for
   new API's.


References
==========

Useful Links:

* `Understanding JSON Schema <http://spacetelescope.github.io/understanding-json-schema/reference/object.html>`_

* `Nova Validation Examples <http://git.openstack.org/cgit/openstack/nova/tree/nova/api/validation>`_

* `JSON Schema on PyPI <https://pypi.python.org/pypi/jsonschema>`_

* `JSON Schema core definitions and terminology <http://tools.ietf.org/html/draft-zyp-json-schema-04>`_

* `JSON Schema Documentation <http://json-schema.org/documentation.html>`_

.. _jsonschema: https://pypi.python.org/pypi/jsonschema