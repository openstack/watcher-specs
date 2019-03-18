..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=============================
API Microversions for Watcher
=============================

https://blueprints.launchpad.net/watcher/+spec/api-microversioning

Problem description
===================

As Watcher evolves and obtains new features which are also represented in API
changes, it's necessary to support new versions of Watcher without breaking
current infrastructure.

Use Cases
---------

As an OpenStack operator, I want to make a request of resource from client v1.1
to Watcher API server with latest version of 1.2 and get an appropriate
response with resource of version 1.1.

As an OpenStack operator, I want to make a request of resource without
specifying API version and get a response with resource of default version.

As an OpenStack operator, I want to make a request of resource with specifying
API version of 1.2 and get a response with resource of 1.2 version.

Proposed change
===============

Watcher API should receive the API version from client
that represents the list resources and their GET/POST/PATCH attributes it can
work with. If user makes a request with wrong API microversion, HTTP 406 Not
Acceptable should be returned.

Since Watcher API uses Pecan + WSME bundle, Watcher microversion validation
should be done in set of special methods which adapt resources to specified
API version. For example, if patch set adds new attributes to resource in
version 1.2 then version 1.1 should exclude these attributes from response.
We will use some parts of `Ironic microversion spec`_ and implementation since
it has Pecan + WSME bundle too.
Let's take a look at possible use cases of communication between Watcher API
and Watcher Client. We will use the term “old Watcher" to refer to a version of
Watcher that predates microversions and has no knowledge of them.

Communication without specifying API microversion (old Watcher)
---------------------------------------------------------------
* The client makes a connection to Watcher, not specifying the
  HTTP header OpenStack-API-Version.
* Watcher does not see the OpenStack-API-Version HTTP header
* Watcher communicates using v1.0 of the REST API, and all communication with
  the client uses that version of the interface.

Communication between old client and new Watcher API
----------------------------------------------------
* The client makes a connection to Watcher, specifying the
  HTTP header OpenStack-API-Version with version 1.0
* Watcher communicates using v1.0 of the REST API, and all communication with
  the client uses that version of the interface.

Communication between new client and new Watcher API
----------------------------------------------------
* The client makes a connection to Watcher, specifying the
  HTTP header OpenStack-API-Version with version 1.1.
* Watcher communicates using v1.1 of the REST API, and all communication with
  the client uses that version of the interface. Response comes along with
  new HTTP header OpenStack-API-Version.

Communication between new client and new Watcher API (with latest microvers)
----------------------------------------------------------------------------
* The client makes a connection to Watcher, supplying ‘latest’ as the
  version in the OpenStack-API-Version HTTP header
* Watcher responds by using the latest API version it supports, and includes
  this in the OpenStack-API-Version header, along with the -Min-
  and -Max- headers.

Negotiation between new client/new API without version specifying
-----------------------------------------------------------------
Watcher client supports versions 1.1 to 1.3, Watcher API supports versions 1.1
to 1.2.

* The user has not specified a version to the client
* The client makes a connection to Watcher, supplying 1.3 as the microversion
  since this is the latest microversion that the client supports.
* Watcher responds with a 406 Not Acceptable, along with the -Min- and -Max-
  headers that it can support (in this case 1.1 and 1.2)
* The client should transparently proceed, having negotiated that both client
  and server will use v1.2. The client should also cache this microversion,
  so that subsequent attempts do not need to renegotiate microversions.

Negotiation between new client/new API with version specifying
--------------------------------------------------------------
Watcher client supports versions 1.1 to 1.3, Watcher API supports versions 1.1
to 1.2.

* The user specifies a particular microversion (e.g. 1.3) that the client
  should use
* The client makes a connection to Watcher, supplying 1.3 as the microversion
* Watcher responds with a 406 Not Acceptable, along with the -Min- and -Max-
  headers that it can support (in this case 1.1 and 1.2)
* The client reports this to the user and exits

Communication between new client/new API with unsupported version
-----------------------------------------------------------------
* The client makes a connection to Watcher, supplying 1.3 as the requested
  microversion.
* Watcher responds with a 406 Not Acceptable, along with the -Min- and -Max-
  headers that it can support (in this case 1.1 and 1.2)
* The client reports this error to the user

To use microservices, client should add OpenStack-API-Version header
to HTTP request before sending requests. python-watcherclient has already
supplied its requests with OpenStack-API-Version header. As of now,
the version is 1.0 and I'd propose to supply 'latest' that would always ask
for the latest API version of Watcher.

What changes requires a new Microversion:

- Changes in query parameters
  Example: adding new parameter, removing old one, changing parameter type.
- Changes in resources
  Example: adding new resource, removing old one.
- Changes in request body
  Example: new field 'audit_description' in POST request body.

This spec also relies on `Microversion Specification`_ as a base for the
proposed changes.

Alternatives
------------
Leave it as is, when user updates Watcher along with new OpenStack release.
It may lead to potential incapability to serve request from legacy clients.

Data model impact
-----------------

None

REST API impact
---------------

Watcher API should accept OpenStack-API-Version HTTP header.

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


Developer impact
----------------

Any future changes to Watcher's REST API (whether that be in the request or
any response) must result in a microversion update, and guarded in the code
appropriately.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  alexchadin (aschadin@sbcloud.ru)

Work Items
----------

* Push OpenStack-API-Version header to API layer.
* Add special filtering methods.
* Implement versions.py module with history of API changes.

Dependencies
============

None

Testing
=======

Appropriate unit and functional tests should be added.

Documentation Impact
====================

None

References
==========

http://specs.openstack.org/openstack/api-wg/guidelines/microversion_specification.html

History
=======

None

.. _Ironic microversion spec: https://specs.openstack.org/openstack/ironic-specs/specs/kilo-implemented/api-microversions.html
.. _Start end time for CONTINUOUS audits: https://blueprints.launchpad.net/watcher/+spec/add-start-end-time-for-continuous-audit
.. _Microversion Specification: http://specs.openstack.org/openstack/api-wg/guidelines/microversion_specification.html
